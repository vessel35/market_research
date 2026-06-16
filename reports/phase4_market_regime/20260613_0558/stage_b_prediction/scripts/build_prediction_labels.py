#!/usr/bin/env python3
"""Stage B (future-regime prediction) — build per-horizon label+feature matrices.

CAUSAL CONTRACT (see regime_prediction_label_spec.md):
  * Features come ONLY from bars <= t (Stage A causal label + causal features + trailing lags).
  * Label is regime[t+h] for h in {3,6,12,24,48} (a SUPERVISED TARGET, never a feature).
  * Drop rows where regime[t] is warmup, where regime[t+h] is unknown_or_warmup, or t+h past end.

This script reads ONLY the Stage A causal file regime_labels.csv. No Phase 2/3 artifact, no DB.
Deterministic; no randomness. Writes one compact gzip CSV matrix per horizon under --outdir.

Usage:
  python stage_b_prediction/scripts/build_prediction_labels.py \\
      --labels stage_a_current_regime/outputs/regime_labels.csv \\
      --outdir stage_b_prediction/outputs \\
      --horizons 3,6,12,24,48
"""
import argparse
import gzip
import hashlib
import io
import json
import os
import sys

import numpy as np
import pandas as pd

CANONICAL = ["strong_up", "strong_down", "transition", "volatile", "range"]
WARMUP = "unknown_or_warmup"

# Causal trailing lags / rolling windows (all use bars <= t only).
REGIME_LAGS = [3, 6]          # one-hot of regime at t-3, t-6
SCORE_ROLL_WINDOWS = [6, 12]  # trailing means of trend/vol scores (bars <= t)
SCORE_DELTA_LAGS = [3, 6]     # score[t] - score[t-lag]


def write_reproducible_gzip(df, path):
    """Write df to a byte-reproducible gzip CSV.

    Determinism requires BOTH: mtime=0 (no embedded timestamp) AND an empty FNAME header
    (pandas/zlib otherwise embeds the output filename, making the gzip path-dependent). With
    deterministic column order + time-sorted rows, the gzip stream is identical on every
    regeneration regardless of output path.
    """
    csv = df.to_csv(index=False).encode("utf-8")
    buf = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buf, mtime=0) as gz:
        gz.write(csv)
    with open(path, "wb") as f:
        f.write(buf.getvalue())


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_features(df):
    """Build causal feature frame (bars <= t only). df is time-sorted, integer-indexed 0..N-1."""
    feat = pd.DataFrame(index=df.index)

    # current regime one-hot (bars <= t: Stage A label of bar t, usable from t+1)
    for c in CANONICAL:
        feat[f"regime_{c}"] = (df["regime"] == c).astype(np.float64)
    # is-warmup flag (so a warmup current bar is representable; such rows are dropped from labels
    # but the flag keeps the feature builder total/explicit)
    feat["regime_is_warmup"] = (df["regime"] == WARMUP).astype(np.float64)

    # current causal scalar features
    feat["regime_confidence"] = df["regime_confidence"].astype(np.float64)
    feat["trend_score"] = df["trend_score"].astype(np.float64)
    feat["volatility_score"] = df["volatility_score"].astype(np.float64)

    # lagged regime one-hots (shift -> uses only past bars)
    for lag in REGIME_LAGS:
        reg_lag = df["regime"].shift(lag)
        for c in CANONICAL:
            feat[f"regime_lag{lag}_{c}"] = (reg_lag == c).astype(np.float64)

    # trailing rolling means of scores (closed on the right at t; min_periods enforced)
    for w in SCORE_ROLL_WINDOWS:
        feat[f"trend_score_roll{w}"] = (
            df["trend_score"].rolling(w, min_periods=w).mean()
        )
        feat[f"volatility_score_roll{w}"] = (
            df["volatility_score"].rolling(w, min_periods=w).mean()
        )

    # short deltas of scores (score[t] - score[t-lag]); causal
    for lag in SCORE_DELTA_LAGS:
        feat[f"trend_score_delta{lag}"] = (
            df["trend_score"] - df["trend_score"].shift(lag)
        )
        feat[f"volatility_score_delta{lag}"] = (
            df["volatility_score"] - df["volatility_score"].shift(lag)
        )

    return feat


def main():
    ap = argparse.ArgumentParser(description="Stage B build per-horizon prediction matrices (causal).")
    ap.add_argument("--labels", required=True, help="path to Stage A regime_labels.csv")
    ap.add_argument("--outdir", required=True, help="output dir for matrices")
    ap.add_argument("--horizons", default="3,6,12,24,48", help="comma-separated horizons in bars")
    args = ap.parse_args()

    horizons = [int(x) for x in args.horizons.split(",") if x.strip()]
    os.makedirs(args.outdir, exist_ok=True)

    usecols = [
        "timestamp", "usable_from_timestamp", "regime", "regime_confidence",
        "trend_score", "volatility_score",
    ]
    df = pd.read_csv(args.labels, usecols=usecols)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp").reset_index(drop=True)

    # strict time order assertion (T4 precondition)
    assert df["timestamp"].is_monotonic_increasing, "timestamps not strictly ordered"
    assert df["timestamp"].is_unique, "duplicate timestamps present"

    feat = build_features(df)
    feature_cols = list(feat.columns)

    # T7 slice-invariance smoke check on a sample predictor (rolling mean):
    # value at an interior index computed on a prefix equals value computed on full series.
    probe_i = len(df) // 2
    w = SCORE_ROLL_WINDOWS[0]
    full_val = df["trend_score"].rolling(w, min_periods=w).mean().iloc[probe_i]
    prefix_val = df["trend_score"].iloc[: probe_i + 1].rolling(w, min_periods=w).mean().iloc[-1]
    if not (pd.isna(full_val) and pd.isna(prefix_val)):
        assert np.isclose(full_val, prefix_val), "T7 slice-invariance failed for rolling feature"

    manifest = {
        "source_labels": os.path.abspath(args.labels),
        "source_labels_sha256": sha256(args.labels),
        "n_rows_total": int(len(df)),
        "feature_columns": feature_cols,
        "horizons": horizons,
        "regime_lags": REGIME_LAGS,
        "score_roll_windows": SCORE_ROLL_WINDOWS,
        "score_delta_lags": SCORE_DELTA_LAGS,
        "canonical_classes": CANONICAL,
        "per_horizon": {},
    }

    reg = df["regime"].copy()
    for h in horizons:
        label = reg.shift(-h)  # regime[t+h]
        # valid row: feature region complete (no NaN in features), current not warmup,
        # future label is a canonical class (not warmup, not NaN past end).
        cur_ok = (df["regime"] != WARMUP)
        fut_ok = label.isin(CANONICAL)
        feat_ok = feat.notna().all(axis=1)
        valid = cur_ok & fut_ok & feat_ok

        # leakage assertion T1: max feature bar index <= t, min label bar index >= t+1.
        # By construction features use shift(>=0)/rolling(right-closed); label uses shift(-h).
        # Assert label index alignment: label at row i is regime at i+h.
        # spot-check a few valid rows
        valid_idx = np.where(valid.values)[0]
        for j in valid_idx[:: max(1, len(valid_idx) // 50)][:50]:
            assert reg.iloc[j + h] == label.iloc[j], "label misalignment (T1)"
            assert j + h > j, "label bar not strictly after t (T1)"

        out = feat.loc[valid].copy()
        out.insert(0, "timestamp", df.loc[valid, "timestamp"].values)
        out.insert(1, "row_index", valid_idx)  # original integer index of t
        out["label_future_regime"] = label.loc[valid].values
        out["horizon_bars"] = h

        out_path = os.path.join(args.outdir, f"prediction_matrix_h{h}.csv.gz")
        # Byte-reproducible gzip (mtime=0, empty FNAME). Column order is deterministic
        # (timestamp,row_index,fixed feature cols,label,horizon) and rows are time-sorted,
        # so the gzip stream is identical on every regeneration.
        write_reproducible_gzip(out, out_path)

        manifest["per_horizon"][str(h)] = {
            "path": os.path.abspath(out_path),
            "n_rows": int(len(out)),
            "n_features": len(feature_cols),
            "label_distribution": out["label_future_regime"].value_counts().to_dict(),
            "sha256": sha256(out_path),
        }
        print(f"[h={h}] rows={len(out)} -> {out_path}")

    man_path = os.path.join(args.outdir, "prediction_matrix_manifest.json")
    with open(man_path, "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    print(f"manifest -> {man_path}")


if __name__ == "__main__":
    sys.exit(main())
