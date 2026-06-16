# Reproducing Phase 4 (run 20260613_0558)

Run all commands from the run directory:

    cd reports/phase4_market_regime/20260613_0558

All steps are deterministic. The committed artifacts
(`stage_a_current_regime/outputs/regime_labels.csv`,
`stage_b_prediction/outputs/prediction_metrics.json`,
`stage_b_prediction/outputs/regime_forecast_h*.csv.gz`) are reproducible within a pinned
same-architecture env (see "Determinism notes" for the cross-platform XGBoost caveat). Their SHA256s
are in `stage_a_current_regime/outputs/provenance.json` and
`stage_b_prediction/outputs/prediction_provenance.json`. Commands use 4-space-indented blocks (the
repo's Markdown-stability rule forbids nested code fences).

## 1. Environment (Python 3.12; tested 3.12.13)

    python3.12 -m venv .venv
    . .venv/bin/activate
    pip install -r reproducibility/requirements.txt
    # pandas 2.1.4, numpy 1.26.3, scipy 1.16.3, scikit-learn 1.9.0, lightgbm 4.6.0, xgboost 2.1.4

## 2. Input

ETH/USDT 5m OHLCV CSV (columns `timestamp,open,high,low,close,volume`; 2024-01-01..2025-12-31).
The exact file's sha256 is `stage_a_current_regime/outputs/provenance.json:input_data_sha256`.
Call the path `$OHLCV`.

## 3. Stage A - current-regime labels

    python stage_a_current_regime/scripts/build_regime_labels.py --input "$OHLCV" \
        --outdir stage_a_current_regime/outputs \
        --git-commit "$(git -C ../../.. rev-parse --short HEAD)" \
        --source-data-path-label ETHUSDT_futures_5min.csv
    python stage_a_current_regime/scripts/validate_regime_labels.py --input "$OHLCV" \
        --labels stage_a_current_regime/outputs/regime_labels.csv \
        --outdir stage_a_current_regime/outputs

Produces:

- `stage_a_current_regime/outputs/regime_labels.csv`
- `stage_a_current_regime/outputs/provenance.json`
- `stage_a_current_regime/outputs/data_quality_report.md`
- `stage_a_current_regime/outputs/validation_results.md`
- `stage_a_current_regime/outputs/regime_label_profile.md`
- `stage_a_current_regime/outputs/regime_transition_matrix.csv`
- `stage_a_current_regime/outputs/regime_duration_distribution.csv`

## 4. Stage B - future-regime prediction

    python stage_b_prediction/scripts/build_prediction_labels.py \
        --labels stage_a_current_regime/outputs/regime_labels.csv \
        --outdir stage_b_prediction/outputs \
        --horizons 3,6,12,24,48
    python stage_b_prediction/scripts/train_predict_regime.py \
        --features stage_b_prediction/outputs \
        --outdir stage_b_prediction/outputs \
        --seed 42 \
        --horizons 3,6,12,24,48

Produces:

- `stage_b_prediction/outputs/prediction_matrix_h{h}.csv.gz` (gitignored; byte-reproducible, gzip mtime=0)
- `stage_b_prediction/outputs/prediction_matrix_manifest.json`
- `stage_b_prediction/outputs/prediction_metrics.json`
- `stage_b_prediction/outputs/regime_forecast_h{h}.csv.gz` (committed; 2025 OOS calibrated forecasts)
- `stage_b_prediction/outputs/prediction_provenance.json`

## Determinism Notes

- Seed 42; gzip `mtime=0` + empty FNAME makes the gzip container byte-reproducible.
- Stage A is fully byte-reproducible: `stage_a_current_regime/outputs/regime_labels.csv` and
  `stage_b_prediction/outputs/prediction_matrix_*.csv.gz` are rule-based / deterministic pandas.
  Independent regeneration matches the provenance sha256 (this was confirmed by an external
  reviewer on a different machine).
- XGBoost is NOT cross-platform bit-reproducible. With the pinned env + seed it is byte-identical
  on the same OS/architecture, but across different OS/arch/CPU the XGBoost forecast
  (`stage_b_prediction/outputs/regime_forecast_*.csv.gz`) and its T3b metrics can differ slightly
  (~1e-3 on accuracy/macro-F1/Brier) from floating-point summation order / build / thread count.
  Cross-platform, expect the metrics to match to ~3 decimals, not bit-for-bit. The canonical
  reproducibility anchors are the input/label sha256 + `stage_b_prediction/outputs/prediction_metrics.json`
  to that tolerance, not the XGBoost forecast bytes across machines. The substantive conclusions
  (short-horizon lift, no lift at h>=24) are stable across runs.
- LightGBM's uncalibrated Brier at h=6/12 can vary ~1e-9 even same-machine (multithreaded
  histogram); rounds identically.
- For true cross-machine bit-identity: fix the full stack in a container (a Dockerfile pinning the
  base image + Python 3.12 + `reproducibility/requirements-lock.txt`) and/or set XGBoost `n_jobs=1`
  and regenerate all horizons. Not done here; it would not change the research conclusions.
- Pinned env: `reproducibility/requirements.txt` pins the 6 top-level libs;
  `reproducibility/requirements-lock.txt` adds their key transitive deps.
- `stage_a_current_regime/outputs/regime_labels.csv` (~52MB) and
  `stage_b_prediction/outputs/regime_forecast_h*.csv.gz` (~13MB) are committed; the
  `stage_b_prediction/outputs/prediction_matrix_*.csv.gz` (~72MB) are gitignored. Regenerate them
  with section 4's first command.

## Scope Reminder

Stage A = validated current-regime classifier. Stage B = research forecast
(auxiliary/probabilistic; short-horizon h=3/6/12 lift over baselines, no lift at h>=24). Neither is
a live-trading signal: whether the forecast improves a strategy is a Phase 3 question
(regime-conditional strategy evaluation), out of scope for Phase 4.
