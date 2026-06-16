# Phase 4 Market Regime Research Index

This run is organized by research stage and by artifact role.

Run directory:

`reports/phase4_market_regime/20260613_0558/`

## Folder Layout

| Folder | Purpose |
|---|---|
| `stage_a_current_regime/docs/` | Stage A method, theory, schema, and leakage-control documents. |
| `stage_a_current_regime/outputs/` | Stage A generated labels, validation reports, provenance, and diagnostics. |
| `stage_a_current_regime/scripts/` | Stage A label generation and validation scripts. |
| `stage_b_prediction/docs/` | Stage B prediction research, target construction, and validation design. |
| `stage_b_prediction/outputs/` | Stage B metrics, provenance, matrix manifest, and forecast artifacts. |
| `stage_b_prediction/scripts/` | Stage B matrix generation and model training scripts. |
| `phase3_handoff/` | Phase 3 consumer contract. |
| `reproducibility/` | Reproduction instructions and dependency pins. |

## Fast Access

| Need | Start here | Then read |
|---|---|---|
| Overall conclusion across Stage A and Stage B | [phase4_final_report.md](phase4_final_report.md) | [phase3_usage_contract.md](phase3_handoff/phase3_usage_contract.md) |
| Current market state labels for Phase 3 joins | [regime_labels.csv](stage_a_current_regime/outputs/regime_labels.csv) | [regime_labels_schema.md](stage_a_current_regime/docs/regime_labels_schema.md) |
| How current regimes are classified | [causal_regime_classifier_spec.md](stage_a_current_regime/docs/causal_regime_classifier_spec.md) | [regime_labeling_pipeline_spec.md](stage_a_current_regime/docs/regime_labeling_pipeline_spec.md) |
| Whether current-regime labels are valid enough to use | [validation_results.md](stage_a_current_regime/outputs/validation_results.md) | [data_quality_report.md](stage_a_current_regime/outputs/data_quality_report.md), [provenance.json](stage_a_current_regime/outputs/provenance.json) |
| Future-regime prediction result | [regime_prediction_results.md](stage_b_prediction/outputs/regime_prediction_results.md) | [prediction_metrics.json](stage_b_prediction/outputs/prediction_metrics.json) |
| Future-regime forecast files | [regime_forecast_h3.csv.gz](stage_b_prediction/outputs/regime_forecast_h3.csv.gz), [regime_forecast_h6.csv.gz](stage_b_prediction/outputs/regime_forecast_h6.csv.gz) | [prediction_provenance.json](stage_b_prediction/outputs/prediction_provenance.json) |
| Reproduce all generated outputs | [REPRODUCE.md](reproducibility/REPRODUCE.md) | [requirements-lock.txt](reproducibility/requirements-lock.txt) |

## Reading Order

1. [phase4_final_report.md](phase4_final_report.md) - final combined conclusion for Stage A and Stage B.
2. [market_regime_definition.md](stage_a_current_regime/docs/market_regime_definition.md) - target concept and regime taxonomy.
3. [selected_primary_regime_framework.md](stage_a_current_regime/docs/selected_primary_regime_framework.md) - selected Stage A framework and rationale.
4. [causal_regime_classifier_spec.md](stage_a_current_regime/docs/causal_regime_classifier_spec.md) - causal current-regime classifier specification.
5. [regime_labels_schema.md](stage_a_current_regime/docs/regime_labels_schema.md) - contract for the Stage A label file.
6. [validation_results.md](stage_a_current_regime/outputs/validation_results.md) - Stage A validation result.
7. [regime_prediction_results.md](stage_b_prediction/outputs/regime_prediction_results.md) - Stage B prediction result.
8. [phase3_usage_contract.md](phase3_handoff/phase3_usage_contract.md) - allowed downstream use in Phase 3.
9. [REPRODUCE.md](reproducibility/REPRODUCE.md) - commands and environment for regeneration.

## Decision Summary

| Area | Decision | Practical implication |
|---|---|---|
| Stage A: current state classification | Accepted as the canonical current market regime label source for Phase 3 joins. | Use [regime_labels.csv](stage_a_current_regime/outputs/regime_labels.csv) as the current-regime label artifact. |
| Stage A method | Uses causal indicators available at or before each bar. | Suitable for historical labeling and live-style current-state classification when data feed timing is respected. |
| Stage B: future state prediction | Useful only as auxiliary probabilistic research output. | Do not replace Stage A labels with Stage B forecasts. |
| Stage B h=3/h=6 | Candidate auxiliary risk or abstention feature. | Can be tested in downstream strategy experiments. |
| Stage B h=12 | Marginal and experimental. | Use only with strict validation. |
| Stage B h=24/h=48 | Excluded for practical use. | Do not use as production decision input. |

## Stage A - Current Market State Classification

Stage A classifies the current market state. It is not a future prediction task.

### Primary Output

| File | Role | Notes |
|---|---|---|
| [regime_labels.csv](stage_a_current_regime/outputs/regime_labels.csv) | Final Stage A label dataset. | Main artifact for Phase 3 joins. |
| [regime_labels_schema.md](stage_a_current_regime/docs/regime_labels_schema.md) | Schema and usage contract for `regime_labels.csv`. | Read before consuming the CSV. |
| [phase3_usage_contract.md](phase3_handoff/phase3_usage_contract.md) | Downstream usage rules. | Defines what Phase 3 may and may not assume. |

### Method And Theory

| File | Role |
|---|---|
| [market_regime_definition.md](stage_a_current_regime/docs/market_regime_definition.md) | Defines market regime concepts and label taxonomy. |
| [regime_framework_research.md](stage_a_current_regime/docs/regime_framework_research.md) | Survey of candidate current-regime frameworks. |
| [regime_framework_selection_matrix.csv](stage_a_current_regime/docs/regime_framework_selection_matrix.csv) | Structured comparison of candidate frameworks. |
| [selected_primary_regime_framework.md](stage_a_current_regime/docs/selected_primary_regime_framework.md) | Selected framework and rationale. |
| [causal_regime_classifier_spec.md](stage_a_current_regime/docs/causal_regime_classifier_spec.md) | Final causal classifier specification. |
| [regime_labeling_pipeline_spec.md](stage_a_current_regime/docs/regime_labeling_pipeline_spec.md) | Pipeline steps used to generate labels. |
| [regime_feature_catalog.csv](stage_a_current_regime/docs/regime_feature_catalog.csv) | Feature catalog used by the classifier. |
| [lookahead_bias_prevention_checklist.md](stage_a_current_regime/docs/lookahead_bias_prevention_checklist.md) | Leakage-prevention checklist. |

### Validation, Quality, And Provenance

| File | Role |
|---|---|
| [validation_results.md](stage_a_current_regime/outputs/validation_results.md) | Validation report. |
| [data_quality_report.md](stage_a_current_regime/outputs/data_quality_report.md) | Input and output data quality summary. |
| [provenance.json](stage_a_current_regime/outputs/provenance.json) | Stage A generation metadata and provenance. |

### Profile And Diagnostics

| File | Role |
|---|---|
| [regime_label_profile.md](stage_a_current_regime/outputs/regime_label_profile.md) | Label distribution and profile summary. |
| [regime_transition_matrix.csv](stage_a_current_regime/outputs/regime_transition_matrix.csv) | Empirical transition matrix between regimes. |
| [regime_duration_distribution.csv](stage_a_current_regime/outputs/regime_duration_distribution.csv) | Duration distribution by regime. |

### Scripts

| File | Role |
|---|---|
| [build_regime_labels.py](stage_a_current_regime/scripts/build_regime_labels.py) | Builds Stage A current-regime labels. |
| [validate_regime_labels.py](stage_a_current_regime/scripts/validate_regime_labels.py) | Validates Stage A labels. |

## Stage B - Future Market State Prediction

Stage B predicts the future value of the Stage A regime label at horizon `h`. It is not a replacement for current-regime classification.

`h` means the forecast horizon in 5-minute bars. For example, `h=3` means 15 minutes ahead, and `h=6` means 30 minutes ahead.

### Results

| File | Role | Notes |
|---|---|---|
| [regime_prediction_results.md](stage_b_prediction/outputs/regime_prediction_results.md) | Main Stage B result report. | Start here for Stage B conclusions. |
| [prediction_metrics.json](stage_b_prediction/outputs/prediction_metrics.json) | Machine-readable prediction metrics. | Contains metrics by horizon. |
| [prediction_provenance.json](stage_b_prediction/outputs/prediction_provenance.json) | Stage B generation metadata and provenance. | Use for audit and reproducibility. |
| [prediction_matrix_manifest.json](stage_b_prediction/outputs/prediction_matrix_manifest.json) | Manifest for generated prediction matrix artifacts. | Matrices are regenerable and gitignored. |

### Forecast Artifacts

| File | Horizon | Practical status |
|---|---:|---|
| [regime_forecast_h3.csv.gz](stage_b_prediction/outputs/regime_forecast_h3.csv.gz) | 3 bars, 15 minutes | Candidate auxiliary feature. |
| [regime_forecast_h6.csv.gz](stage_b_prediction/outputs/regime_forecast_h6.csv.gz) | 6 bars, 30 minutes | Candidate auxiliary feature. |
| [regime_forecast_h12.csv.gz](stage_b_prediction/outputs/regime_forecast_h12.csv.gz) | 12 bars, 60 minutes | Experimental only. |
| [regime_forecast_h24.csv.gz](stage_b_prediction/outputs/regime_forecast_h24.csv.gz) | 24 bars, 120 minutes | Excluded from practical use. |
| [regime_forecast_h48.csv.gz](stage_b_prediction/outputs/regime_forecast_h48.csv.gz) | 48 bars, 240 minutes | Excluded from practical use. |

### Method And Validation Design

| File | Role |
|---|---|
| [regime_prediction_research.md](stage_b_prediction/docs/regime_prediction_research.md) | Research notes for future-regime prediction. |
| [regime_prediction_label_spec.md](stage_b_prediction/docs/regime_prediction_label_spec.md) | Future target construction contract. |
| [regime_prediction_validation_plan.md](stage_b_prediction/docs/regime_prediction_validation_plan.md) | Walk-forward validation design and leakage controls. |

### Scripts

| File | Role |
|---|---|
| [build_prediction_labels.py](stage_b_prediction/scripts/build_prediction_labels.py) | Builds future target labels from Stage A labels. |
| [train_predict_regime.py](stage_b_prediction/scripts/train_predict_regime.py) | Trains and evaluates future-regime prediction models. |

## Reproducibility And Environment

| File | Role |
|---|---|
| [REPRODUCE.md](reproducibility/REPRODUCE.md) | End-to-end reproduction instructions. |
| [requirements.txt](reproducibility/requirements.txt) | Direct Python dependencies. |
| [requirements-lock.txt](reproducibility/requirements-lock.txt) | Locked Python dependency versions used for this run. |

## Consumer Guidance

Use Stage A when the question is:

- "What is the current market state at timestamp `t`?"
- "Which current-regime label should be joined into Phase 3?"
- "Which regime was active when a strategy signal occurred?"

Use Stage B only when the question is:

- "What is the model-implied probability of the Stage A label at `t+h`?"
- "Should a strategy reduce exposure because near-term regime uncertainty is high?"
- "Can forecast confidence be used as an auxiliary risk or abstention feature?"

Do not use Stage B to overwrite, backfill, or redefine Stage A current-regime labels.

