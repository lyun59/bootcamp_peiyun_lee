# TSM Next-Day Price Direction Forecast

## Summary

This project predicts whether Taiwan Semiconductor Manufacturing Company (TSM, NYSE ADR)
will close **up or down** on the next trading day, using only prior market data (price and
volume). It is framed as a binary classification problem: given today's and recent
historical features, will tomorrow's close be higher or lower than today's?

The problem matters because a reliable one-day directional edge — even a modest one — can
inform daily buy / hold / sell decisions for an individual investor. TSM is a good target:
one of the most liquid semiconductor names, with clean daily data and enough volatility
that the direction is non-trivial.

**The headline finding is a well-quantified negative:** the model scores at chance
(accuracy ~50%, AUC 0.53 with a 95% bootstrap CI of 0.46–0.59). The value of the project is
the *reproducible, risk-aware process* around that honest conclusion — see
`docs/project_summary.md` for the plain-language version.

## Stakeholder

**Persona** — an individual / retail investor (or junior analyst) who wants a simple,
explainable directional call rather than a black-box forecast. They care about
**actionability**, **explainability**, and **reproducibility**.

## Quick start (from a fresh clone)

```bash
git clone <repo-url> && cd project
python -m venv .venv && source .venv/bin/activate   # or: conda create -n tsm python=3.11
pip install -r requirements.txt
cp .env.example .env                                # edit if you change ticker/range
python -c "from src.modeling import run_all, load_modeling_data; print(run_all(load_modeling_data())['clf']['auc'])"
```

Reproduce the whole project by running `notebooks/project_pipeline.ipynb` top to bottom,
or explore individual stages in the notebooks under `notebooks/`.

## Lifecycle → where the work lives

| Stage | Deliverable / file(s) |
|------|------------------------|
| 01 Problem framing & scoping | `README.md`, `docs/stakeholder-memo.md` |
| 02 Tooling setup | `src/config.py`, `.env.example`, `.gitignore`, `requirements.txt` |
| 03 Python fundamentals | `src/utils.py`, `notebooks/python_fundamentals_summary.ipynb` |
| 04 Data acquisition & ingestion | `notebooks/project_pipeline.ipynb`, `data/raw/tsm.csv` |
| 05 Data storage | env-driven IO in `src/config.py`, `data/processed/tsm.parquet` |
| 06 Data preprocessing | `src/cleaning.py`, `data/processed/tsm_processed.csv` |
| 07 Outliers & risk | `src/outliers.py`, `docs/outliers.md` |
| 08 Exploratory data analysis | `src/eda.py`, `notebooks/eda.ipynb` |
| 09 Feature engineering | `src/features.py`, `data/processed/tsm_featured.csv` |
| 10a Modeling — regression | `src/modeling.py`, `notebooks/modeling_regression.ipynb` |
| 10b Modeling — classification | `src/modeling.py`, `notebooks/modeling_classification.ipynb` |
| 11 Evaluation & risk | `src/evaluation.py`, `notebooks/evaluation.ipynb` |
| 12 Delivery design | `reports/final_report.md`, `reports/images/` |
| 13 Productization | `app.py`, `src/prediction.py`, `model/model.pkl`, `docs/handoff-summary.md` |
| 14 Deployment & monitoring | `docs/monitoring_plan.md`, `docs/handoff_plan.md` |
| 15 Orchestration & system design | `docs/orchestration_plan.md`, `src/run_step.py` |
| 16 Lifecycle review | `docs/lifecycle_framework_guide.md`, `docs/project_summary.md` |

A fuller one-line-per-stage map is in `docs/lifecycle_framework_guide.md`.

## Data

- **Source:** Yahoo Finance, fetched programmatically with `yfinance` (no API key).
- **Ticker / range:** `TSM`, configurable via `.env` (see `.env.example`); default
  `2020-01-01` → `2025-12-31`.
- **Raw vs processed:** `data/raw/` (as-ingested, never overwritten) and `data/processed/`
  (parquet columnar copy, cleaned CSV, featured CSV).

## Features

Nine leakage-safe, stationary predictors are used for modeling (see `src/features.py` for
the builder functions and their rationales):

`return_1d`, `return_5d`, `return_20d` (momentum), `close_to_ma_5`, `close_to_ma_20`,
`ma_5_20_spread` (trend position), `volume_ratio_20` (volume surge), `intraday_range`,
`overnight_gap`. Price-scaled `ma_5`/`ma_20`/`vol_20` are computed in Stage 06 but
**excluded** from the model to avoid leaking the price level.

## Model & API

The classification model is a `StandardScaler → LogisticRegression` pipeline, trained on a
chronological split (first 80% train, last 20% test — no shuffling) and, for deployment,
refit on the full dataset and saved to `model/model.pkl`.

**Serve it:**

```bash
python app.py        # listens on http://127.0.0.1:5001 (5000 is macOS AirPlay Receiver)
```

**Call it:**

```bash
curl -X POST http://127.0.0.1:5001/predict \
     -H "Content-Type: application/json" \
     -d '{"features": {"return_1d": -0.006, "return_5d": 0.041, "return_20d": 0.032,
          "close_to_ma_5": 0.008, "close_to_ma_20": 0.021, "ma_5_20_spread": 0.013,
          "volume_ratio_20": 0.588, "intraday_range": 0.019, "overnight_gap": -0.004}}'

curl http://127.0.0.1:5001/health
curl -X POST http://127.0.0.1:5001/run_full_analysis
```

Routes: `GET /health`, `POST /predict` (accepts a feature list or dict; returns
`probability_up`, `direction`, `direction_label`), `POST /run_full_analysis` (returns both
tracks' metrics). Malformed input returns a JSON error and HTTP 400.

## Run one step from the CLI

```bash
python src/run_step.py --step train    # fit + save model/model.pkl (idempotent)
```

See `docs/orchestration_plan.md` for the full 7-task pipeline, dependencies and retry
policy.

## Results & risk summary

- Classification: accuracy **0.500** (baseline 0.524), AUC **0.530** (95% bootstrap CI
  **0.464–0.587**).
- Regression (next-day return): R² ≈ 0, RMSE 0.0253 ≈ the return's own std.
- Robust across a random forest and a momentum-only feature set — the "no edge" conclusion
  is not an artefact of one modelling choice.

Full narrative and charts: `reports/final_report.md`. Assumptions, limitations and next
steps: `docs/handoff-summary.md` and `docs/project_summary.md`.

## Assumptions & risks (carried across stages)

- Features use only information known by today's close; the split is chronological.
- Daily returns are fat-tailed and slightly skewed, so Gaussian uncertainty is optimistic —
  bootstrap intervals are used instead.
- The relationship is assumed stable across the sample; a regime shift would invalidate a
  single global model.
- `.env` is git-ignored; only `.env.example` is committed. No real keys are stored.
