# Orchestration & System Design — TSM Project

Decomposing the end-to-end pipeline into schedulable tasks, their dependencies, and a
reliability plan. All paths are relative to the `project/` root.

## 1. Task list (inputs → outputs)

| # | Task | Inputs | Outputs | Idempotent? |
| --- | --- | --- | --- | --- |
| 1 | **ingest** | yfinance (network) | `data/raw/tsm.csv` | Yes — overwrites with a fresh pull of the same range |
| 2 | **store** | `data/raw/tsm.csv` | `data/processed/tsm.parquet` | Yes — same raw → same parquet |
| 3 | **clean** | `data/raw/tsm.csv` | `data/processed/tsm_processed.csv` | Yes — deterministic transforms |
| 4 | **features** | `data/processed/tsm_processed.csv` | `data/processed/tsm_featured.csv` | Yes — pure functions in `src/features.py` |
| 5 | **train** | `data/processed/tsm_featured.csv` | `model/model.pkl` | Yes — logistic regression is deterministic |
| 6 | **evaluate** | `data/processed/tsm_featured.csv`, `model/model.pkl` | `reports/images/*.png` | Yes — fixed seed, deterministic |
| 7 | **report** | `reports/images/*`, metrics | `reports/final_report.md` | Mostly — narrative reviewed by a human |

## 2. Dependencies (DAG)

```
ingest -> store -> clean -> features -> train -> evaluate -> report
                  \-----> features -------^
```

- `store`, `clean` both depend only on `ingest`'s output; `store` and `clean` could run
  in **parallel**.
- `features` needs `clean` (and could also read `store`'s parquet — same data, different
  format).
- `train` needs `features`; `evaluate` needs `features` + `train`; `report` needs
  `evaluate`'s figures.

| Task | Depends on |
| --- | --- |
| ingest | — |
| store | ingest |
| clean | ingest |
| features | clean (or store) |
| train | features |
| evaluate | features, train |
| report | evaluate |

## 3. Logging & checkpoints

- **Checkpoints are the artifact files themselves** — each task's output file is the
  checkpoint; a downstream task re-runs only if its input artifact exists and is newer.
- **Logging** follows the pattern in `src/run_step.py`: `start`, `rows in/out`, `params`,
  and `artifact path` at INFO level, errors at ERROR level with the failing input named.
- A task that fails leaves no half-written artifact: write to a temp file, then atomically
  rename into place (keeps checkpoints valid).

## 4. Failure points & retry policy

| Failure | Where | Retry policy |
| --- | --- | --- |
| Network down (yfinance) | ingest | 3 retries with 30s linear backoff; then alert Data on-call |
| Schema change | clean/features | Fail fast (no retry); diff schema and pin ingest |
| Missing warm-up rows | features | Non-fatal — drop the first ~20 rows as designed |
| Model file missing | train/evaluate | Re-run `train` first (deterministic), then retry |
| Disk full / write error | any | 3 retries with backoff, then page Platform on-call |

## 5. Right-sizing automation

- **Automate now:** `train` (via `python src/run_step.py --step train`) and `evaluate` —
  they are offline, deterministic, and cheap. `ingest`/`store`/`clean`/`features` already
  run headlessly from `notebooks/project_pipeline.ipynb`.
- **Keep manual:** `report` (the narrative needs a human to sanity-check the numbers and
  tone before a stakeholder sees it) and the retrain-*decision* (shadow-testing and
  promotion stay human-gated — see `docs/monitoring_plan.md`).
- **Rationale:** the project scope is a single daily batch, so a lightweight, script-driven
  pipeline (functions + `run_step.py`) is the right size; a full orchestrator (Airflow/
  Prefect) would add operational cost without benefit at this scale.
