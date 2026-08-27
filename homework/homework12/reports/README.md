# Homework 12 — Reporting & Delivery Design

This directory holds the final, stakeholder-ready reporting artifacts for the TSM
next-day direction forecast project.

## Contents

| File | Purpose |
| --- | --- |
| `final_report.md` | The written Markdown report — Executive Summary, charts + interpretation, assumptions & risks, sensitivity analysis, and decision implications. |
| `images/` | Exported charts (PNG) referenced by the report. |
| `../data/processed/sensitivity_table.csv` | The sensitivity table behind the tornado chart. |

## Charts

- `images/risk_return.png` — Risk–Return scatter by scenario
- `images/return_by_scenario.png` — Return by scenario (bar)
- `images/metricA_over_time.png` — MetricA over time by category (line)
- `images/tornado_assumptions.png` — Sensitivity tornado (Δ return vs baseline)

## How to regenerate

1. Run the notebook
   `homework12_results-reporting-delivery-design_submission.ipynb` (top to bottom).
2. The notebook writes `reports/images/*.png` and
   `data/processed/sensitivity_table.csv`.
3. `final_report.md` is the human-readable summary of those outputs.

## Key numbers

- Baseline (median impute): return 12%, volatility 18%, Sharpe 0.56
- Mean imputation: return 11%, volatility 18.5%, Sharpe 0.49
- 3σ outlier rule: return 13.5%, volatility 19%, Sharpe 0.61
