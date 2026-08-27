# Lifecycle Framework Guide — TSM Next-Day Direction Forecast

One row per lifecycle stage, mapping the stage to the file(s) in this repo that hold its
work, plus the one-line decision made there. This is the "how we got here" map for anyone
inheriting the project.

| Stage | What was decided | Where it lives |
| --- | --- | --- |
| 01 Problem framing & scoping | Frame as *binary next-day direction* for a retail investor; value explainability + reproducibility | `README.md`, `docs/stakeholder-memo.md` |
| 02 Tooling setup | Env-driven config, git-ignored `.env`, reproducible `requirements.txt` | `src/config.py`, `.env.example`, `.gitignore`, `requirements.txt` |
| 03 Python fundamentals | Small, non-mutating pandas/NumPy helpers | `src/utils.py`, `notebooks/python_fundamentals_summary.ipynb` |
| 04 Data acquisition | Pull TSM OHLCV from yfinance (keyless); pin the date range | `notebooks/project_pipeline.ipynb` (Stage 04), `data/raw/tsm.csv` |
| 05 Data storage | CSV for raw, Parquet for processed; never overwrite raw | `src/config.py`, `data/processed/tsm.parquet` |
| 06 Preprocessing | Clean column names, add base features + `target` label | `src/cleaning.py`, `data/processed/tsm_processed.csv` |
| 07 Outliers & risk | Prefer winsorizing over dropping (keep real extreme moves) | `src/outliers.py`, `docs/outliers.md` |
| 08 EDA | Profile distributions; confirm fat-tailed, slightly skewed returns | `src/eda.py`, `notebooks/eda.ipynb` |
| 09 Feature engineering | Build stationary ratio/return features, not price levels | `src/features.py`, `data/processed/tsm_featured.csv` |
| 10a Modeling — regression | Linear regression on next-day *return*; diagnose residuals | `src/modeling.py`, `notebooks/modeling_regression.ipynb` |
| 10b Modeling — classification | Logistic pipeline on next-day *direction* (the goal) | `src/modeling.py`, `notebooks/modeling_classification.ipynb` |
| 11 Evaluation & risk | Bootstrap CIs + scenario analysis; quantify the no-skill result | `src/evaluation.py`, `notebooks/evaluation.ipynb` |
| 12 Delivery design | Stakeholder report with charts, assumptions, sensitivity | `reports/final_report.md`, `reports/images/` |
| 13 Productization | Refactor to `src/prediction.py`, save model, serve via Flask | `app.py`, `src/prediction.py`, `model/model.pkl`, `docs/handoff-summary.md` |
| 14 Deployment & monitoring | Define data/model/system/business metrics + owners | `docs/monitoring_plan.md`, `docs/handoff_plan.md` |
| 15 Orchestration | Decompose into 7 tasks; refactor `train` to a CLI step | `docs/orchestration_plan.md`, `src/run_step.py` |
| 16 Lifecycle review | Make the whole chain legible as one project | this guide, `docs/project_summary.md`, `README.md` |

## One-sentence throughline

The project went from *"can we predict TSM's next-day direction?"* to a **served, monitored,
documented model** whose honest headline finding is that the one-day signal is at chance —
and whose real value is the reproducible, risk-aware process around that conclusion.
