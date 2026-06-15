# Reproducing Phase 4 (run 20260613_0558)

All steps are deterministic. The committed artifacts (`regime_labels.csv`,
`prediction_metrics.json`, `regime_forecast_h*.csv.gz`) are reproducible; their SHA256s are in
`provenance.json` / `prediction_provenance.json`. Commands use 4-space-indented blocks (the repo's
Markdown-stability rule forbids nested code fences).

## 1. Environment (Python 3.12; tested 3.12.13)

    python3.12 -m venv .venv
    . .venv/bin/activate
    pip install -r requirements.txt
    # pandas 2.1.4, numpy 1.26.3, scipy 1.16.3, scikit-learn 1.9.0, lightgbm 4.6.0, xgboost 2.1.4

## 2. Input

ETH/USDT 5m OHLCV CSV (columns `timestamp,open,high,low,close,volume`; 2024-01-01..2025-12-31).
The exact file's sha256 is `provenance.json:input_data_sha256`. Call the path `$OHLCV`.

## 3. Stage A — current-regime labels

    python build_regime_labels.py --input "$OHLCV" --outdir . \
        --git-commit "$(git -C . rev-parse --short HEAD)" \
        --source-data-path-label ETHUSDT_futures_5min.csv
    python validate_regime_labels.py --input "$OHLCV" --labels regime_labels.csv --outdir .

Produces `regime_labels.csv` (byte-reproducible; sha256 in `provenance.json`), `provenance.json`,
`data_quality_report.md`, and `validation_results.md` (17 tests, all PASS).

## 4. Stage B — future-regime prediction

    python build_prediction_labels.py --labels regime_labels.csv --outdir . --horizons 3,6,12,24,48
    python train_predict_regime.py --features . --outdir . --seed 42 --horizons 3,6,12,24,48

Produces `prediction_matrix_h{h}.csv.gz` (gitignored; byte-reproducible, gzip mtime=0),
`prediction_metrics.json`, `regime_forecast_h{h}.csv.gz` (committed; 2025 OOS calibrated forecasts),
and `prediction_provenance.json`.

## Determinism notes

- Seed 42; gzip `mtime=0` + empty FNAME → byte-reproducible gzip. XGBoost (the forecast model) and
  all macro-F1 / calibrated-Brier metrics are bit-reproducible.
- Known minor: LightGBM's *uncalibrated* Brier at h=6/12 can vary ~1e-9 across runs (multithreaded
  histogram); it rounds identically and does not affect the forecast or any reported metric.
- `regime_labels.csv` (~52MB) and `regime_forecast_h*.csv.gz` (~13MB) are committed; the
  `prediction_matrix_*.csv.gz` (~72MB) are gitignored — regenerate with §4's first command.

## Scope reminder

Stage A = validated current-regime classifier. Stage B = **research** forecast
(auxiliary/probabilistic; short-horizon h=3/6/12 lift over baselines, no lift at h>=24). Neither is
a live-trading signal: whether the forecast improves a strategy is a **Phase 3** question
(regime-conditional strategy evaluation), out of scope for Phase 4.
