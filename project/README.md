# TSM Next-Day Price Direction Forecast

## Summary

This project predicts whether Taiwan Semiconductor Manufacturing Company (TSM, NYSE
ADR) will close **up or down** on the next trading day, using only prior market data
(price and volume). It is framed as a binary classification problem: given today's
and recent historical features, will tomorrow's close be higher or lower than
today's?

The problem matters because a reliable one-day directional edge — even a modest one
— can inform daily buy / hold / sell decisions for an individual investor. TSM is a
good target: it is one of the most liquid semiconductor names, with clean and
consistent daily data, and enough volatility that the direction is non-trivial
(not a series that is simply "always up" or "always down").

## Stakeholder

**Persona** — an individual / retail investor (or a junior analyst) who reviews a
short daily briefing and wants a simple, explainable directional call rather than a
black-box price forecast. They care about:

- **Actionability** — a clear up/down signal they can act on before the next open.
- **Explainability** — *why* the model says up or down (which features drove it).
- **Reproducibility** — the same data and code should produce the same result on
  any machine.

## Goals → lifecycle → deliverables

| Goal | Lifecycle stage | Deliverable |
|------|-----------------|-------------|
| Define the problem and who it serves | 01 Problem Framing & Scoping | `README.md`, `docs/stakeholder-memo.md` |
| Reproducible project skeleton | 02 Tooling Setup | folder scaffold, `.env`, `requirements.txt`, `src/config.py` |
| Reusable Python / NumPy / pandas utilities | 03 Python Fundamentals | `src/utils.py`, `notebooks/python_fundamentals_summary.ipynb` |
| Programmatic data acquisition | 04 Data Acquisition & Ingestion | `notebooks/project_pipeline.ipynb`, `data/raw/tsm.csv` |
| Reproducible storage & reload | 05 Data Storage | env-driven IO, `data/raw` + `data/processed` |
| Clean, model-ready features | 06 Data Preprocessing | `src/cleaning.py`, processed dataset |
| Documented outlier handling | 07 Outliers & Risk Assumptions | `src/outliers.py`, sensitivity analysis |
| Understand data patterns & relationships | 08 Exploratory Data Analysis | `src/eda.py`, `notebooks/eda.ipynb` |
| Model-ready engineered features | 09 Feature Engineering | `src/features.py`, feature table below |

## Data

- **Source:** Yahoo Finance, fetched programmatically with `yfinance` (no API key).
- **Ticker:** `TSM` (NYSE ADR).
- **Frequency:** daily OHLCV.
- **Range:** configurable via `.env` (see `.env.example`); default `2020-01-01` to
  `2025-12-31`.

## Data Storage

Raw and processed data live in separate folders so the as-ingested data is never
overwritten:

- **`data/raw/`** — unmodified, as-ingested data (`tsm.csv` from the API pull).
- **`data/processed/`** — transformed outputs (`tsm.parquet` columnar copy,
  `tsm_processed.csv` after cleaning, and `tsm_featured.csv` after feature
  engineering).

### Formats

- **CSV** — human-readable and portable; used for the raw ingest.
- **Parquet** — columnar binary format, smaller and faster, and preserves dtypes;
  used for the processed layer (requires `pyarrow`).

### Environment-driven paths

Storage paths are read from `.env` via `src/config.py` (`DATA_DIR_RAW`,
`DATA_DIR_PROCESSED`), so the same code runs on any machine without edits.
`.env` is git-ignored; `.env.example` is the committed template.

## Outlier handling

Outlier detection, assumptions, and risks are documented in
`docs/outliers.md`; the reusable code lives in `src/outliers.py`.

## Features

Two stages contribute features. Stage 06 (`src/cleaning.py`) adds the base
features and the label; Stage 09 (`src/features.py`) adds the engineered set.
All are computed on returns or price ratios (not raw levels) because the price
series trends over the sample.

| Feature | Definition | Why it helps |
|---------|-----------|--------------|
| `return_1d` | `close.pct_change(1)` | immediate one-day direction (Stage 06) |
| `ma_5`, `ma_20` | 5- and 20-day rolling mean of close | local trend level (Stage 06) |
| `vol_20` | 20-day rolling std of close | volatility regime (Stage 06) |
| `target` | 1 if next close > close, else 0 | the next-day direction label |
| `return_5d`, `return_20d` | `close.pct_change(n)` | multi-horizon momentum; short/long can disagree |
| `close_to_ma_5`, `close_to_ma_20` | `close / rolling_mean − 1` | trend position (above/below own average) |
| `ma_5_20_spread` | `(ma_5 − ma_20) / ma_20` | short-vs-long trend (crossover) |
| `volume_ratio_20` | `volume / rolling-mean(volume, 20)` | volume surge on big moves |
| `intraday_range` | `(high − low) / close` | same-day volatility |
| `overnight_gap` | `open / prev_close − 1` | overnight news that sets the session |

`target` is the label; the rest are candidate predictors. Each function's
docstring in `src/features.py` carries the same rationale, so the reasoning
travels with the code.
