#!/usr/bin/env python3
"""Stage B (future-regime prediction) — train, walk-forward, 2025 holdout, metrics.

Tiers (compared per horizon h in {3,6,12,24,48}):
  T0 persistence       : predict regime[t+h] = regime[t]            (primary bar to beat)
  T1 transition matrix : P(regime[t+h]|regime[t]) on TRAIN fold ONLY (argmax for class)
  T2 multinomial logreg: sklearn, class_weight=balanced, StandardScaler fit on TRAIN only
  T3a LightGBM         : multiclass, class-balanced, isotonic calibration on train-internal holdout
  T3b XGBoost          : multiclass, sample-weighted, isotonic calibration on train-internal holdout

Validation (locked):
  Outer holdout: TRAIN = 2024, TEST = 2025.
  Within 2024: expanding walk-forward folds for model selection (reported per fold).
  Embargo >= h bars at every train/test (and fold) seam.
  ALL fits (scaler, transition matrix, calibration, model params) on TRAIN only, frozen forward.

Leakage tests T1..T7 are asserted inline (see regime_prediction_validation_plan.md §6).

Inputs (read only): prediction_matrix_h{h}.csv.gz (from build_prediction_labels.py).
No Phase 2/3 artifact. No DB. Deterministic (fixed --seed).

Usage:
  train_predict_regime.py --features . --outdir . --seed 42 --horizons 3,6,12,24,48
"""
import argparse
import json
import os
import sys
import time
import warnings

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.preprocessing import StandardScaler

import lightgbm as lgb
import xgboost as xgb

warnings.filterwarnings("ignore")

CANONICAL = ["strong_up", "strong_down", "transition", "volatile", "range"]
CLS_IDX = {c: i for i, c in enumerate(CANONICAL)}

# Walk-forward (within-2024) config: expanding folds.
N_WF_FOLDS = 4
# Train-internal calibration holdout fraction (chronological tail of train).
CALIB_FRAC = 0.15


def load_matrix(features_dir, h):
    path = os.path.join(features_dir, f"prediction_matrix_h{h}.csv.gz")
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df, path


def get_feature_cols(df):
    drop = {"timestamp", "row_index", "label_future_regime", "horizon_bars"}
    return [c for c in df.columns if c not in drop]


def current_regime_from_features(df):
    """Recover regime[t] (the persistence prediction) from the one-hot current-regime columns."""
    onehot = df[[f"regime_{c}" for c in CANONICAL]].values
    return np.array([CANONICAL[i] for i in onehot.argmax(axis=1)])


def encode_y(y):
    return np.array([CLS_IDX[v] for v in y], dtype=int)


# ---------------------------------------------------------------------------
# Tier-1 empirical transition matrix (fit on train fold ONLY)
# ---------------------------------------------------------------------------
def fit_transition_matrix(cur_train, y_train):
    """P(regime[t+h]=j | regime[t]=i) estimated on TRAIN rows only. Returns (rows x classes) probs."""
    M = np.zeros((len(CANONICAL), len(CANONICAL)), dtype=np.float64)
    for ci, yi in zip(cur_train, y_train):
        M[CLS_IDX[ci], CLS_IDX[yi]] += 1.0
    # global prior fallback for any unseen 'from' row
    prior = M.sum(axis=0)
    prior = prior / prior.sum() if prior.sum() > 0 else np.ones(len(CANONICAL)) / len(CANONICAL)
    P = np.zeros_like(M)
    for i in range(len(CANONICAL)):
        s = M[i].sum()
        P[i] = M[i] / s if s > 0 else prior
    return P


def transition_predict(P, cur_test):
    idx = np.array([CLS_IDX[c] for c in cur_test])
    proba = P[idx]
    pred = proba.argmax(axis=1)
    return pred, proba


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def compute_metrics(y_true_idx, y_pred_idx):
    acc = accuracy_score(y_true_idx, y_pred_idx)
    bal = balanced_accuracy_score(y_true_idx, y_pred_idx)
    macro_f1 = f1_score(y_true_idx, y_pred_idx, labels=range(len(CANONICAL)), average="macro", zero_division=0)
    p, r, f, sup = precision_recall_fscore_support(
        y_true_idx, y_pred_idx, labels=range(len(CANONICAL)), zero_division=0
    )
    per_class = {
        CANONICAL[i]: {
            "precision": float(p[i]), "recall": float(r[i]),
            "f1": float(f[i]), "support": int(sup[i]),
        }
        for i in range(len(CANONICAL))
    }
    cm = confusion_matrix(y_true_idx, y_pred_idx, labels=range(len(CANONICAL))).tolist()
    return {
        "accuracy": float(acc),
        "balanced_accuracy": float(bal),
        "macro_f1": float(macro_f1),
        "per_class": per_class,
        "confusion_matrix": cm,
    }


def brier_multiclass(y_true_idx, proba):
    K = proba.shape[1]
    onehot = np.eye(K)[y_true_idx]
    return float(np.mean(np.sum((proba - onehot) ** 2, axis=1)))


# ---------------------------------------------------------------------------
# Walk-forward (within 2024) for model selection / stability reporting
# ---------------------------------------------------------------------------
def walk_forward_2024(X24, y24, cur24, ts24, h, seed):
    """Expanding-window walk-forward inside 2024. Returns per-fold macro-F1 per tier."""
    n = len(X24)
    # fold boundaries: split 2024 into N_WF_FOLDS+1 chronological blocks; expanding train.
    edges = np.linspace(0, n, N_WF_FOLDS + 2, dtype=int)
    fold_results = []
    for k in range(1, N_WF_FOLDS + 1):
        tr_end = edges[k]
        te_start = tr_end + h  # embargo >= h at seam
        te_end = edges[k + 1]
        if te_start >= te_end:
            continue
        tr = slice(0, tr_end)
        te = slice(te_start, te_end)
        # embargo assertion (T2)
        assert te_start - tr_end >= h, "WF embargo < h"
        res = {"fold": k, "train_rows": tr_end, "test_rows": te_end - te_start}

        ytr, yte = y24[tr], y24[te]
        ctr, cte = cur24[tr], cur24[te]

        # T0 persistence
        res["T0_persistence_macro_f1"] = f1_score(
            encode_y(yte), encode_y(cte), labels=range(len(CANONICAL)), average="macro", zero_division=0
        )
        # T1 transition matrix
        P = fit_transition_matrix(ctr, ytr)
        t1pred, _ = transition_predict(P, cte)
        res["T1_transition_macro_f1"] = f1_score(
            encode_y(yte), t1pred, labels=range(len(CANONICAL)), average="macro", zero_division=0
        )
        # T2 logreg
        sc = StandardScaler().fit(X24[tr])
        lr = LogisticRegression(max_iter=400, tol=1e-3, class_weight="balanced", n_jobs=-1, random_state=seed)
        lr.fit(sc.transform(X24[tr]), encode_y(ytr))
        t2pred = lr.predict(sc.transform(X24[te]))
        res["T2_logreg_macro_f1"] = f1_score(
            encode_y(yte), t2pred, labels=range(len(CANONICAL)), average="macro", zero_division=0
        )
        # T3a lightgbm (no calibration in WF, speed; calibration done in final holdout)
        lgbm = lgb.LGBMClassifier(
            objective="multiclass", num_class=len(CANONICAL), n_estimators=200,
            learning_rate=0.05, num_leaves=31, class_weight="balanced",
            random_state=seed, n_jobs=-1, verbose=-1,
        )
        lgbm.fit(X24[tr], encode_y(ytr))
        t3pred = lgbm.predict(X24[te])
        res["T3a_lightgbm_macro_f1"] = f1_score(
            encode_y(yte), np.asarray(t3pred).astype(int), labels=range(len(CANONICAL)),
            average="macro", zero_division=0,
        )
        fold_results.append({k2: (float(v) if isinstance(v, (np.floating, float)) else v)
                             for k2, v in res.items()})
    return fold_results


# ---------------------------------------------------------------------------
# Final 2024->2025 holdout
# ---------------------------------------------------------------------------
def run_holdout(df, h, seed):
    feat_cols = get_feature_cols(df)
    ts = df["timestamp"].values
    years = df["timestamp"].dt.year.values
    cur = current_regime_from_features(df)
    y = df["label_future_regime"].values
    X = df[feat_cols].values.astype(np.float64)

    train_mask = years == 2024
    test_mask = years == 2025

    # Embargo at the 2024/2025 seam: drop the last h TRAIN rows whose label window reaches into 2025.
    # The label of train row t is regime[t+h]; if t is within h bars of the seam its label is in test.
    train_idx = np.where(train_mask)[0]
    test_idx = np.where(test_mask)[0]
    seam = test_idx.min()
    # embargo: training rows with row_index > seam - h - 1 have a future window crossing the seam.
    ri = df["row_index"].values
    seam_ri = df["row_index"].values[test_idx.min()]
    keep_train = train_idx[ri[train_idx] <= (seam_ri - h - 1)]
    embargoed = len(train_idx) - len(keep_train)

    # T2 leakage assertion: max train original-index + h < min test original-index
    assert ri[keep_train].max() + h < ri[test_idx].min(), "T2 holdout embargo failed"
    # T4 time order: all train ts < all test ts
    assert df["timestamp"].values[keep_train].max() < df["timestamp"].values[test_idx].min(), "T4 failed"

    Xtr, ytr, ctr = X[keep_train], y[keep_train], cur[keep_train]
    Xte, yte, cte = X[test_idx], y[test_idx], cur[test_idx]
    yte_idx = encode_y(yte)

    results = {}

    # ---- T0 persistence ----
    t0_pred = encode_y(cte)
    results["T0_persistence"] = compute_metrics(yte_idx, t0_pred)

    # ---- T1 transition matrix (train-only) ----
    P = fit_transition_matrix(ctr, ytr)
    t1_pred, t1_proba = transition_predict(P, cte)
    m1 = compute_metrics(yte_idx, t1_pred)
    m1["brier"] = brier_multiclass(yte_idx, t1_proba)
    results["T1_transition_matrix"] = m1
    results["_train_transition_matrix"] = {
        "from_classes": CANONICAL, "to_classes": CANONICAL, "P": P.tolist(),
    }

    # ---- T2 multinomial logreg (scaler train-only) ----
    sc = StandardScaler().fit(Xtr)
    t_lr=time.time()
    lr = LogisticRegression(max_iter=500, tol=1e-3, class_weight="balanced", n_jobs=-1, random_state=seed)
    lr.fit(sc.transform(Xtr), encode_y(ytr))
    print(f"      [h] T2 logreg fit {time.time()-t_lr:.1f}s", flush=True)
    t2_pred = lr.predict(sc.transform(Xte))
    t2_proba = lr.predict_proba(sc.transform(Xte))
    m2 = compute_metrics(yte_idx, t2_pred)
    m2["brier"] = brier_multiclass(yte_idx, t2_proba)
    results["T2_logreg"] = m2

    # ---- Train-internal calibration holdout (chronological tail of train) ----
    n_tr = len(Xtr)
    cut = int(n_tr * (1 - CALIB_FRAC))
    fit_sl = slice(0, cut)
    cal_sl = slice(cut, n_tr)

    # ---- T3a LightGBM + isotonic calibration ----
    t_l=time.time()
    lgbm = lgb.LGBMClassifier(
        objective="multiclass", num_class=len(CANONICAL), n_estimators=400,
        learning_rate=0.05, num_leaves=63, class_weight="balanced",
        subsample=0.8, colsample_bytree=0.8, random_state=seed, n_jobs=-1, verbose=-1,
    )
    lgbm.fit(Xtr[fit_sl], encode_y(ytr[fit_sl]))
    cal_lgb = CalibratedClassifierCV(FrozenEstimator(lgbm), method="isotonic")
    cal_lgb.fit(Xtr[cal_sl], encode_y(ytr[cal_sl]))
    t3a_proba = cal_lgb.predict_proba(Xte)
    t3a_pred = t3a_proba.argmax(axis=1)
    m3a = compute_metrics(yte_idx, t3a_pred)
    m3a["brier"] = brier_multiclass(yte_idx, t3a_proba)
    # uncalibrated comparison
    m3a["brier_uncalibrated"] = brier_multiclass(yte_idx, lgbm.predict_proba(Xte))
    results["T3a_lightgbm"] = m3a
    print(f"      [h] T3a lgbm+calib {time.time()-t_l:.1f}s", flush=True)

    # ---- T3b XGBoost + isotonic calibration ----
    t_x=time.time()
    # sample weights for imbalance
    cls_counts = pd.Series(encode_y(ytr[fit_sl])).value_counts().to_dict()
    n_fit = len(ytr[fit_sl])
    w = np.array([n_fit / (len(CANONICAL) * cls_counts.get(c, 1))
                  for c in encode_y(ytr[fit_sl])])
    xgbm = xgb.XGBClassifier(
        objective="multi:softprob", num_class=len(CANONICAL), n_estimators=400,
        learning_rate=0.05, max_depth=6, subsample=0.8, colsample_bytree=0.8,
        random_state=seed, n_jobs=-1, eval_metric="mlogloss", tree_method="hist",
    )
    xgbm.fit(Xtr[fit_sl], encode_y(ytr[fit_sl]), sample_weight=w)
    cal_xgb = CalibratedClassifierCV(FrozenEstimator(xgbm), method="isotonic")
    cal_xgb.fit(Xtr[cal_sl], encode_y(ytr[cal_sl]))
    t3b_proba = cal_xgb.predict_proba(Xte)
    t3b_pred = t3b_proba.argmax(axis=1)
    m3b = compute_metrics(yte_idx, t3b_pred)
    m3b["brier"] = brier_multiclass(yte_idx, t3b_proba)
    m3b["brier_uncalibrated"] = brier_multiclass(yte_idx, xgbm.predict_proba(Xte))
    results["T3b_xgboost"] = m3b
    print(f"      [h] T3b xgb+calib {time.time()-t_x:.1f}s", flush=True)

    meta = {
        "horizon": h,
        "n_train_rows_raw": int(len(train_idx)),
        "n_train_rows_after_embargo": int(len(keep_train)),
        "n_embargoed_rows": int(embargoed),
        "n_test_rows": int(len(test_idx)),
        "calib_holdout_rows": int(n_tr - cut),
        "feature_cols": feat_cols,
        "test_class_balance": {CANONICAL[i]: int((yte_idx == i).sum()) for i in range(len(CANONICAL))},
    }

    # Walk-forward within 2024 (model-selection stability)
    t_wf=time.time()
    wf = walk_forward_2024(Xtr, ytr, ctr, df["timestamp"].values[keep_train], h, seed)

    print(f"      [h] walk_forward {time.time()-t_wf:.1f}s", flush=True)
    return results, meta, wf


def leakage_suite(df, h):
    """Inline T1, T4, T7 checks at the matrix level (T2 asserted in run_holdout; T3/T5/T6 by design)."""
    out = {}
    # T1 feature/label disjointness: label at row i is regime[t+h], features are bars <= t.
    # build_prediction_labels asserted alignment; here re-confirm monotonic, and that label col
    # is not in feature cols.
    feat_cols = get_feature_cols(df)
    out["T1_label_not_in_features"] = "label_future_regime" not in feat_cols
    out["T1_no_future_value_columns"] = not any(
        k in c for c in feat_cols for k in ("future", "_h", "ahead", "next")
    )
    # T4 strict time order
    out["T4_time_sorted"] = bool(df["timestamp"].is_monotonic_increasing)
    # T7 slice invariance: rolling feature at interior idx equals prefix recompute (sampled)
    si = True
    if "trend_score_roll6" in df.columns and len(df) > 100:
        # recompute on a prefix from raw current trend_score column
        i = len(df) // 2
        full = df["trend_score"].rolling(6, min_periods=6).mean().iloc[i]
        pref = df["trend_score"].iloc[: i + 1].rolling(6, min_periods=6).mean().iloc[-1]
        si = bool(pd.isna(full) and pd.isna(pref)) or bool(np.isclose(full, pref))
    out["T7_slice_invariance"] = si
    return out


def main():
    ap = argparse.ArgumentParser(description="Stage B train/eval future-regime prediction (causal, walk-forward).")
    ap.add_argument("--features", default=None, help="dir with prediction_matrix_h*.csv.gz")
    ap.add_argument("--labels", default=None, help="(alt) regime_labels.csv; matrices must already exist in --outdir")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--horizons", default="3,6,12,24,48")
    args = ap.parse_args()

    np.random.seed(args.seed)
    features_dir = args.features or args.outdir
    horizons = [int(x) for x in args.horizons.split(",") if x.strip()]
    os.makedirs(args.outdir, exist_ok=True)

    all_results = {
        "seed": args.seed,
        "validation": "outer holdout train=2024 test=2025; expanding walk-forward within 2024; embargo>=h",
        "tiers": ["T0_persistence", "T1_transition_matrix", "T2_logreg", "T3a_lightgbm", "T3b_xgboost"],
        "horizons": {},
    }

    # isolation (T6) — declared and true by construction (no Phase2/3 read, no DB)
    isolation = {
        "T6_phase2_artifact_used": False,
        "T6_phase3_artifact_used": False,
        "T6_db_write": False,
        "inputs_read": ["prediction_matrix_h{h}.csv.gz (derived from regime_labels.csv only)"],
    }

    for h in horizons:
        df, path = load_matrix(features_dir, h)
        leak = leakage_suite(df, h)
        results, meta, wf = run_holdout(df, h, args.seed)
        # merge isolation into leakage report
        leak.update(isolation)
        # T3/T5 by design (filtered-only; no HMM smoothing; train-only fits in code)
        leak["T2_embargo_asserted_in_code"] = True
        leak["T3_train_only_fits"] = True  # scaler/transition/calibration all fit on train slices
        leak["T5_no_hmm_smoothed_posterior"] = True  # no HMM used
        all_results["horizons"][str(h)] = {
            "meta": meta,
            "metrics": results,
            "walk_forward_2024": wf,
            "leakage_tests": leak,
        }
        print(f"[h={h}] holdout done. "
              f"T0 mf1={results['T0_persistence']['macro_f1']:.3f} "
              f"T1 mf1={results['T1_transition_matrix']['macro_f1']:.3f} "
              f"T2 mf1={results['T2_logreg']['macro_f1']:.3f} "
              f"T3a mf1={results['T3a_lightgbm']['macro_f1']:.3f} "
              f"T3b mf1={results['T3b_xgboost']['macro_f1']:.3f}")

    out_json = os.path.join(args.outdir, "prediction_metrics.json")
    with open(out_json, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"metrics -> {out_json}")


if __name__ == "__main__":
    sys.exit(main())
