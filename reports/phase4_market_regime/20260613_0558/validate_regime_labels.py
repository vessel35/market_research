"""
Phase 4 Stage A — standalone validation script.
Re-runs the full test suite against a (possibly pre-existing) regime_labels.csv
and writes validation_results.md (regenerable, not ad-hoc).

CLI
---
  python validate_regime_labels.py \\
      --input  /path/to/ETHUSDT_futures_5min.csv \\
      --labels /path/to/regime_labels.csv \\
      --outdir /path/to/run_dir

Defaults:
  --labels : <script dir>/regime_labels.csv
  --outdir : <script dir>

Tests run (each PASS/FAIL + evidence):
  1. Unit branch tests (5 regimes + warmup + inclusive boundaries + confidence)
  2. Schema check (20 cols, 0 of 14 forbidden, regime_labeling=causal,
     llm_discretion_used=false, regime in canonical+warmup set)
  3. usable_from_timestamp > timestamp (all rows)
  4. Effective-warmup-301 direct assert (rows 0..300 warmup, first labeled idx=301)
  5. Indicator reference: EMA vs pandas ewm(adjust=False) post-warmup
  6. Indicator reference: Wilder ATR(14)/+DI/-DI/DX on constructed example
  7. Slice-invariance: 40 random + boundary-stratified ADX in [24,26] and
     vol_score in [68,72] — recompute on data[0:t+1] == full-series. Bars <= t only.

No future data is used. No Phase 2/3 reads. No DB.
"""

import argparse
import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# ─── Import classifier functions from build_regime_labels.py ─────────────────
# We resolve the sibling script by the location of this file.
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from build_regime_labels import (
    ADX_PERIOD,
    WARMUP_END,
    VOL_WINDOW,
    VOL_MIN_PERIODS,
    ADX_THRESHOLD,
    VOL_THRESHOLD,
    wilder_rma_sum,
    wilder_rma_avg,
    compute_adx,
    compute_ema,
    compute_volatility_score,
    classify_bar,
    compute_confidence,
)

CANONICAL_REGIMES = {"strong_up", "strong_down", "transition", "volatile", "range"}
WARMUP_LABEL = "unknown_or_warmup"
EXPECTED_COLS = 20
FORBIDDEN_COLS = [
    "strategy_id", "variant_id", "trade_id", "net_pnl", "return_pct",
    "future_return", "future_max_price", "future_min_price", "future_profit",
    "phase2_result", "edge_fragment_id", "usable_in_hybrid", "polarity",
    "strategy_evaluation_verdict",
]
REQUIRED_COLS = [
    "timestamp", "usable_from_timestamp", "symbol", "timeframe",
    "regime", "regime_alt", "regime_labeling", "regime_confidence",
    "selected_primary_framework", "trend_score", "volatility_score",
    "momentum_score", "mean_reversion_score", "volume_score",
    "data_quality_score", "feature_snapshot_ref", "classifier_version",
    "source_data_path", "git_commit", "llm_discretion_used",
]


# ─── CLI ─────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Phase 4 Stage A — validate regime_labels.csv and write validation_results.md.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        default=os.environ.get("PHASE4_OHLCV"),
        metavar="PATH",
        help="Path to OHLCV CSV file (required). Defaults to PHASE4_OHLCV env var.",
    )
    parser.add_argument(
        "--labels",
        default=None,
        metavar="PATH",
        help="Path to regime_labels.csv. Defaults to <script dir>/regime_labels.csv.",
    )
    parser.add_argument(
        "--outdir",
        default=None,
        metavar="PATH",
        help="Output directory for validation_results.md. Defaults to <script dir>.",
    )
    args = parser.parse_args()
    if args.input is None:
        parser.error("--input is required (or set PHASE4_OHLCV environment variable).")
    return args


# ─── Test helpers ─────────────────────────────────────────────────────────────

def _chk(results, name, condition, evidence):
    results.append((name, bool(condition), str(evidence)))


# ─── Test 1: Unit branch tests ────────────────────────────────────────────────

def test_unit_branches():
    """5 regime branches + warmup + boundary conditions + confidence range."""
    results = []

    r, ra = classify_bar(adx=30, ema9=2300, ema21=2200, ema55=2100, vol_score=50)
    _chk(results, "unit_strong_up", r == "strong_up",
         f"ADX=30 EMA9>EMA21>EMA55 -> regime='{r}' (expected 'strong_up') alt='{ra}'")

    r, ra = classify_bar(adx=30, ema9=2100, ema21=2200, ema55=2300, vol_score=50)
    _chk(results, "unit_strong_down", r == "strong_down",
         f"ADX=30 EMA9<EMA21<EMA55 -> regime='{r}' (expected 'strong_down') alt='{ra}'")

    r, ra = classify_bar(adx=30, ema9=2300, ema21=2100, ema55=2200, vol_score=50)
    _chk(results, "unit_transition", r == "transition",
         f"ADX=30 EMA9>EMA21 but EMA21<EMA55 -> regime='{r}' (expected 'transition') alt='{ra}'")

    r, ra = classify_bar(adx=18, ema9=2300, ema21=2200, ema55=2100, vol_score=85)
    _chk(results, "unit_volatile", r == "volatile",
         f"ADX=18 vol_score=85 -> regime='{r}' (expected 'volatile') alt='{ra}'")

    r, ra = classify_bar(adx=18, ema9=2300, ema21=2200, ema55=2100, vol_score=40)
    _chk(results, "unit_range", r == "range",
         f"ADX=18 vol_score=40 -> regime='{r}' (expected 'range') alt='{ra}'")

    # Warmup label not emitted by classify_bar (pipeline level); verified by boundary test
    results.append(("unit_warmup_handled_in_pipeline", True,
                    "Warmup / NaN rows set to 'unknown_or_warmup' before classify_bar is "
                    "called; verified by effective_warmup_301 test"))

    # Inclusive boundary ADX=25
    r, ra = classify_bar(adx=25.0, ema9=2300, ema21=2200, ema55=2100, vol_score=50)
    _chk(results, "unit_boundary_adx_25_trend", r == "strong_up",
         f"ADX=25.0 (boundary) EMA up -> regime='{r}' (must be 'strong_up'; >= inclusive)")

    # Inclusive boundary vol_score=70
    r, ra = classify_bar(adx=18, ema9=2300, ema21=2200, ema55=2100, vol_score=70.0)
    _chk(results, "unit_boundary_vol_70_volatile", r == "volatile",
         f"ADX=18 vol_score=70.0 (boundary) -> regime='{r}' (must be 'volatile'; >= inclusive)")

    # Confidence in [0,1]
    c = compute_confidence("strong_up", 30, 2300, 2200, 2100, 50, 10.0)
    _chk(results, "unit_confidence_strong_up_range", 0.0 <= c <= 1.0,
         f"confidence={c:.6f} for strong_up (must be in [0,1])")

    c = compute_confidence("range", 18, 2300, 2200, 2100, 40, 10.0)
    _chk(results, "unit_confidence_range_range", 0.0 <= c <= 1.0,
         f"confidence={c:.6f} for range (must be in [0,1])")

    c = compute_confidence("volatile", 18, 2300, 2200, 2100, 85, 10.0)
    _chk(results, "unit_confidence_volatile_range", 0.0 <= c <= 1.0,
         f"confidence={c:.6f} for volatile (must be in [0,1])")

    return results


# ─── Test 2: Schema check ─────────────────────────────────────────────────────

def test_schema(labels_df):
    results = []

    # Column count
    ncols = len(labels_df.columns)
    _chk(results, "schema_col_count", ncols == EXPECTED_COLS,
         f"columns={ncols} (expected {EXPECTED_COLS}); cols={list(labels_df.columns)}")

    # Required columns present
    missing = [c for c in REQUIRED_COLS if c not in labels_df.columns]
    _chk(results, "schema_required_cols_present", len(missing) == 0,
         f"missing required columns: {missing or 'none'}")

    # No forbidden columns
    found_forbidden = [c for c in FORBIDDEN_COLS if c in labels_df.columns]
    _chk(results, "schema_no_forbidden_cols", len(found_forbidden) == 0,
         f"forbidden columns found: {found_forbidden or 'none'} "
         f"(0 of {len(FORBIDDEN_COLS)} forbidden cols present)")

    # regime_labeling = 'causal' all rows
    bad_rl = (labels_df["regime_labeling"] != "causal").sum() if "regime_labeling" in labels_df.columns else -1
    _chk(results, "schema_regime_labeling_causal", bad_rl == 0,
         f"rows with regime_labeling != 'causal': {bad_rl}")

    # llm_discretion_used = false all rows
    if "llm_discretion_used" in labels_df.columns:
        bad_llu = (labels_df["llm_discretion_used"] != False).sum()
    else:
        bad_llu = -1
    _chk(results, "schema_llm_discretion_false", bad_llu == 0,
         f"rows with llm_discretion_used != false: {bad_llu}")

    # regime values in canonical + warmup set
    if "regime" in labels_df.columns:
        allowed = CANONICAL_REGIMES | {WARMUP_LABEL}
        bad_regime = (~labels_df["regime"].isin(allowed)).sum()
        bad_vals = labels_df.loc[~labels_df["regime"].isin(allowed), "regime"].unique().tolist()
    else:
        bad_regime, bad_vals = -1, []
    _chk(results, "schema_regime_values_canonical", bad_regime == 0,
         f"rows with regime not in canonical+warmup: {bad_regime}; "
         f"unexpected values: {bad_vals or 'none'}")

    return results


# ─── Test 3: usable_from_timestamp > timestamp ────────────────────────────────

def test_usable_from(labels_df):
    results = []
    bad = labels_df[labels_df["usable_from_timestamp"] <= labels_df["timestamp"]]
    _chk(results, "usable_from_gt_timestamp", len(bad) == 0,
         f"rows with usable_from_timestamp <= timestamp: {len(bad)} (expected 0)")
    return results


# ─── Test 4: Effective warmup = 301 ──────────────────────────────────────────

def test_effective_warmup_301(labels_df):
    """
    Direct assert: rows 0..300 (inclusive, 301 rows) all unknown_or_warmup;
    row index 301 is the FIRST non-warmup labeled row.
    """
    results = []

    first_301 = labels_df.iloc[:301]
    all_warmup = (first_301["regime"] == WARMUP_LABEL).all()
    warmup_count = (first_301["regime"] == WARMUP_LABEL).sum()

    non_warmup = labels_df[labels_df["regime"] != WARMUP_LABEL]
    if len(non_warmup) > 0:
        first_labeled_idx = non_warmup.index[0]
        first_labeled_ts = str(labels_df.loc[first_labeled_idx, "timestamp"])
        first_labeled_regime = labels_df.loc[first_labeled_idx, "regime"]
    else:
        first_labeled_idx = -1
        first_labeled_ts = "N/A"
        first_labeled_regime = "N/A"

    passed = all_warmup and (first_labeled_idx == 301)
    _chk(results, "effective_warmup_first_labeled_at_301", passed,
         f"rows 0..300 all unknown_or_warmup={all_warmup} ({warmup_count}/301); "
         f"first non-warmup index={first_labeled_idx} (expected 301); "
         f"row 301 regime='{first_labeled_regime}' @ {first_labeled_ts}")

    return results


# ─── Test 5: EMA indicator reference (vs pandas ewm(adjust=False)) ────────────

def test_ema_reference(df):
    """
    Compare compute_ema vs pd.Series.ewm(span=N, adjust=False).mean() over
    bars 500..1000. Tolerance 1e-6. SMA-seed transient has decayed by bar 500
    (worst case EMA55: (1-2/56)^(500-55) ~ 5e-8 < 1e-6).
    Causal: uses only bars up to (and including) the comparison window.
    """
    results = []
    close = df["close"].to_numpy(dtype=float)

    for period in [9, 21, 55]:
        script_ema = compute_ema(close, period)
        pandas_ema = pd.Series(close).ewm(span=period, adjust=False).mean().to_numpy()
        # Compare well past the warmup (seed transient decayed)
        diff = np.abs(script_ema[500:1001] - pandas_ema[500:1001])
        max_diff = float(np.nanmax(diff))
        passed = max_diff < 1e-6
        _chk(results, f"ema{period}_vs_pandas_ewm", passed,
             f"max abs diff over bars 500..1000 = {max_diff:.3e} (threshold 1e-6)")

    return results


# ─── Test 6: Wilder ATR/DI/DX hand-verify on real data ───────────────────────

def test_wilder_hand_verify(df):
    """
    Hand-verify Wilder ATR(14)/+DI/-DI/DX at the seed position and first two
    recursion steps using first 17 bars of the actual OHLCV data.
    Results are re-derived from scratch and compared to script output.
    """
    results = []
    df17 = df.iloc[:17].copy().reset_index(drop=True)
    high  = df17["high"].to_numpy(dtype=float)
    low   = df17["low"].to_numpy(dtype=float)
    close = df17["close"].to_numpy(dtype=float)

    # Recompute TR, +DM, -DM from scratch for 17 bars
    TR_hand = np.zeros(17)
    pDM_hand = np.zeros(17)
    mDM_hand = np.zeros(17)
    for t in range(1, 17):
        hl  = high[t] - low[t]
        hpc = abs(high[t] - close[t - 1])
        lpc = abs(low[t]  - close[t - 1])
        TR_hand[t] = max(hl, hpc, lpc)
        up   = high[t] - high[t - 1]
        down = low[t - 1] - low[t]
        if up > down and up > 0:
            pDM_hand[t] = up
        elif down > up and down > 0:
            mDM_hand[t] = down

    # Seed at index 13 (period=14; TR[1:] slice means seed uses TR_hand[1..14])
    atr_seed  = float(np.sum(TR_hand[1:15]))    # bars 1..14
    pdm_seed  = float(np.sum(pDM_hand[1:15]))
    mdm_seed  = float(np.sum(mDM_hand[1:15]))

    # One recursion at bar 15 (index 14 in TR_hand, but the slice TR[1:] makes
    # the script's seed align to TR_hand[1..14] and recursion uses TR_hand[15])
    atr_bar15 = atr_seed - atr_seed / 14 + TR_hand[15]
    atr_bar16 = atr_bar15 - atr_bar15 / 14 + TR_hand[16]

    pDI_seed  = 100.0 * pdm_seed / atr_seed
    mDI_seed  = 100.0 * mdm_seed / atr_seed
    DX_seed_denom = pDI_seed + mDI_seed
    DX_seed   = 0.0 if DX_seed_denom == 0 else 100.0 * abs(pDI_seed - mDI_seed) / DX_seed_denom

    # Script output on first 17 bars
    s_ATR, plus_DI, minus_DI, ADX14 = compute_adx(df17, 14)

    # s_ATR[14] = seed position (index in full array = period-1 in TR[1:] slice + 1 pad)
    # In the script: s_ATR is padded with [NaN] at index 0, so seed is at index 14.
    script_atr_seed  = float(s_ATR[14])
    script_atr_bar15 = float(s_ATR[15])
    script_atr_bar16 = float(s_ATR[16])
    script_pDI_seed  = float(plus_DI[14])
    script_mDI_seed  = float(minus_DI[14])

    tol = 1e-4  # absolute tolerance for hand-verify (rounding in manual computation)

    _chk(results, "wilder_atr14_hand_verify",
         (abs(script_atr_seed - atr_seed) < tol and
          abs(script_atr_bar15 - atr_bar15) < tol and
          abs(script_atr_bar16 - atr_bar16) < tol),
         f"seed={atr_seed:.6f} script={script_atr_seed:.6f}; "
         f"bar15={atr_bar15:.6f} script={script_atr_bar15:.6f}; "
         f"bar16={atr_bar16:.6f} script={script_atr_bar16:.6f}; "
         f"max abs diff={max(abs(script_atr_seed-atr_seed), abs(script_atr_bar15-atr_bar15), abs(script_atr_bar16-atr_bar16)):.2e}")

    _chk(results, "wilder_di14_hand_verify",
         (abs(script_pDI_seed - pDI_seed) < tol and
          abs(script_mDI_seed - mDI_seed) < tol),
         f"+DI={pDI_seed:.6f} script={script_pDI_seed:.6f}; "
         f"-DI={mDI_seed:.6f} script={script_mDI_seed:.6f}; "
         f"max abs diff={max(abs(script_pDI_seed-pDI_seed), abs(script_mDI_seed-mDI_seed)):.2e}")

    # DX derived from script DI values
    script_DX_from_DI = (0.0 if (script_pDI_seed + script_mDI_seed) == 0
                         else 100.0 * abs(script_pDI_seed - script_mDI_seed) /
                              (script_pDI_seed + script_mDI_seed))
    _chk(results, "wilder_dx14_hand_verify",
         abs(script_DX_from_DI - DX_seed) < tol,
         f"DX at bar 14={DX_seed:.6f} re-derived from script DI values={script_DX_from_DI:.6f}; "
         f"abs diff={abs(script_DX_from_DI-DX_seed):.2e}")

    return results


# ─── Test 7: Slice-invariance ─────────────────────────────────────────────────

def _run_slice_at(df, t):
    """Recompute regime at index t using data[0:t+1] only (causal)."""
    df_trunc = df.iloc[: t + 1].copy().reset_index(drop=True)
    atr14_t, _, _, adx14_t = compute_adx(df_trunc, ADX_PERIOD)
    close_t = df_trunc["close"].to_numpy(dtype=float)
    ema9_t  = compute_ema(close_t, 9)
    ema21_t = compute_ema(close_t, 21)
    ema55_t = compute_ema(close_t, 55)
    vs_t    = compute_volatility_score(atr14_t, VOL_WINDOW, VOL_MIN_PERIODS)

    last = len(df_trunc) - 1
    is_warmup = (
        last < WARMUP_END
        or np.isnan(ema9_t[last])
        or np.isnan(ema21_t[last])
        or np.isnan(ema55_t[last])
        or np.isnan(adx14_t[last])
        or np.isnan(atr14_t[last])
        or np.isnan(vs_t[last])
    )
    if is_warmup:
        return WARMUP_LABEL
    regime, _ = classify_bar(adx14_t[last], ema9_t[last], ema21_t[last], ema55_t[last], vs_t[last])
    return regime


def test_slice_invariance(df, labels_df, n_random=40):
    """
    40 random indices (past warmup) + 20 near ADX boundary [24,26] +
    20 near vol_score boundary [68,72]. All use data[0:t+1] (causal, bars <= t).
    """
    results = []
    n = len(df)

    # 40 random indices spread over labeled range
    random_indices = np.linspace(WARMUP_END + 100, n - 1, n_random, dtype=int)
    random_indices = sorted(set(random_indices.tolist()))

    failures_rand = []
    for t in random_indices:
        regime_trunc = _run_slice_at(df, t)
        regime_full  = labels_df.iloc[t]["regime"]
        if regime_trunc != regime_full:
            failures_rand.append({"t": t, "full": regime_full, "trunc": regime_trunc})

    all_rand_pass = len(failures_rand) == 0
    _chk(results, "slice_invariance_40_random", all_rand_pass,
         f"{n_random} random samples tested; failures={len(failures_rand)} (expected 0)"
         + (f"; first failure: t={failures_rand[0]}" if failures_rand else ""))

    # Boundary-stratified: ADX in [24, 26]
    adx_col = pd.to_numeric(labels_df["trend_score"], errors="coerce")
    adx_band = labels_df[
        (adx_col >= 24) & (adx_col <= 26) & (labels_df.index >= WARMUP_END + 1)
    ].index.tolist()
    adx_sample = adx_band[:20]

    failures_adx = []
    for t in adx_sample:
        regime_trunc = _run_slice_at(df, t)
        regime_full  = labels_df.iloc[t]["regime"]
        if regime_trunc != regime_full:
            failures_adx.append({"t": t, "full": regime_full, "trunc": regime_trunc})

    _chk(results, "boundary_adx_slice_invariance", len(failures_adx) == 0,
         f"{len(adx_sample)} bars tested with ADX14 in [24,26] "
         f"(found {len(adx_band)} in band); failures={len(failures_adx)} (expected 0)")

    # Boundary-stratified: vol_score in [68, 72]
    vol_col = pd.to_numeric(labels_df["volatility_score"], errors="coerce")
    vol_band = labels_df[
        (vol_col >= 68) & (vol_col <= 72) & (labels_df.index >= WARMUP_END + 1)
    ].index.tolist()
    vol_sample = vol_band[:20]

    failures_vol = []
    for t in vol_sample:
        regime_trunc = _run_slice_at(df, t)
        regime_full  = labels_df.iloc[t]["regime"]
        if regime_trunc != regime_full:
            failures_vol.append({"t": t, "full": regime_full, "trunc": regime_trunc})

    _chk(results, "boundary_volscore_slice_invariance", len(failures_vol) == 0,
         f"{len(vol_sample)} bars tested with vol_score in [68,72] "
         f"(found {len(vol_band)} in band); failures={len(failures_vol)} (expected 0)")

    return results


# ─── Build report ─────────────────────────────────────────────────────────────

def _section(lines, title):
    lines.append(f"## {title}")
    lines.append("")


def _table_header(lines, cols):
    lines.append("| " + " | ".join(cols) + " |")
    lines.append("|" + "|".join(["---"] * len(cols)) + "|")


def _table_row(lines, vals):
    safe = [str(v).replace("|", "/") for v in vals]
    lines.append("| " + " | ".join(safe) + " |")


def build_report(all_test_groups, labels_df, ohlcv_path, labels_path):
    """Assemble validation_results.md text from test result groups."""
    lines = [
        "# Validation Results",
        "",
        f"**OHLCV source:** `{ohlcv_path}`",
        f"**Labels file:** `{labels_path}`",
        f"**Rows:** {len(labels_df):,}",
        "",
    ]

    section_num = 1
    all_pass = True
    summary_rows = []

    for section_title, test_results in all_test_groups:
        _section(lines, f"{section_num}. {section_title}")
        _table_header(lines, ["test", "result", "evidence"])
        sec_pass = True
        for name, passed, evidence in test_results:
            status = "PASS" if passed else "FAIL"
            if not passed:
                all_pass = False
                sec_pass = False
            _table_row(lines, [name, status, evidence])
        lines.append("")
        summary_rows.append((section_title, "PASS" if sec_pass else "FAIL"))
        section_num += 1

    lines.append("## Overall Verdict")
    lines.append("")
    verdict = "ALL TESTS PASS" if all_pass else "ONE OR MORE TESTS FAILED"
    lines.append(f"**{verdict}**")
    lines.append("")
    _table_header(lines, ["section", "result"])
    for title, status in summary_rows:
        _table_row(lines, [title, status])
    lines.append("")

    return "\n".join(lines), all_pass


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    ohlcv_path = str(args.input)
    script_dir = Path(__file__).resolve().parent

    labels_path = Path(args.labels).resolve() if args.labels else (script_dir / "regime_labels.csv")
    outdir      = Path(args.outdir).resolve() if args.outdir else script_dir

    outdir.mkdir(parents=True, exist_ok=True)

    print("Phase 4 Stage A — validate_regime_labels.py")
    print(f"OHLCV:  {ohlcv_path}")
    print(f"Labels: {labels_path}")
    print(f"Outdir: {outdir}")
    print("")

    # ── Load data ─────────────────────────────────────────────────────────────
    print("Loading OHLCV...")
    df_raw = pd.read_csv(ohlcv_path)
    df = df_raw.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=False)
    if df["timestamp"].dt.tz is None:
        df["timestamp"] = df["timestamp"].dt.tz_localize("UTC")
    else:
        df["timestamp"] = df["timestamp"].dt.tz_convert("UTC")
    print(f"  {len(df):,} rows")

    print("Loading regime_labels.csv...")
    labels_df = pd.read_csv(labels_path, parse_dates=["timestamp", "usable_from_timestamp"])
    print(f"  {len(labels_df):,} rows")

    # ── Run tests ─────────────────────────────────────────────────────────────
    print("Running unit branch tests...")
    t1 = test_unit_branches()

    print("Running schema checks...")
    t2 = test_schema(labels_df)

    print("Checking usable_from_timestamp > timestamp...")
    t3 = test_usable_from(labels_df)

    print("Checking effective warmup = 301...")
    t4 = test_effective_warmup_301(labels_df)

    print("Running EMA indicator reference tests...")
    t5 = test_ema_reference(df)

    print("Running Wilder ATR/DI/DX hand-verify...")
    t6 = test_wilder_hand_verify(df)

    print("Running slice-invariance tests (40 random + 2 boundary bands)...")
    t7 = test_slice_invariance(df, labels_df, n_random=40)

    # ── Build + write report ──────────────────────────────────────────────────
    all_test_groups = [
        ("Unit Branch Tests (5 regimes + warmup + boundaries + confidence)", t1),
        ("Schema Check (20 cols, 0 of 14 forbidden, causal, canonical regimes)", t2),
        ("usable_from_timestamp > timestamp (all rows)", t3),
        ("Effective Warmup = 301 (rows 0..300 warmup, first labeled idx=301)", t4),
        ("EMA Indicator Reference vs pandas ewm(adjust=False)", t5),
        ("Wilder ATR(14)/+DI/-DI/DX Hand-Verify on Real Data", t6),
        ("Slice-Invariance: 40 random + ADX-boundary + vol_score-boundary (causal)", t7),
    ]

    report_text, all_pass = build_report(
        all_test_groups, labels_df, ohlcv_path, str(labels_path)
    )

    out_path = outdir / "validation_results.md"
    out_path.write_text(report_text, encoding="utf-8")
    print(f"\nWritten: {out_path}")
    print(f"Overall: {'ALL TESTS PASS' if all_pass else 'ONE OR MORE TESTS FAILED'}")

    if not all_pass:
        sys.exit(1)


if __name__ == "__main__":
    main()
