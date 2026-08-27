# Handoff Plan — TSM Next-Day Direction Model

The deployment path and the runbook an on-call operator would follow. Complements
`monitoring_plan.md`, which lists the metrics and thresholds each step references.

## Deployment path

- **Artifacts:** model `model/model.pkl` (joblib), code in `src/`, API in `app.py`,
  dependencies in `requirements.txt`.
- **Build:** `pip install -r requirements.txt`; copy `.env.example` to `.env`.
- **Start:** `python app.py` (serves `/health`, `/predict`, `/run_full_analysis` on
  port 5001 — 5000 is taken by macOS AirPlay Receiver).
- **Promote:** new model versions ship as `model_vN.pkl`; the active one is copied to
  `model/model.pkl` only after a one-week shadow test.

## On-call runbook (bullets)

- **"data stale" alert** → open the ingest log, confirm the market feed, rerun
  `src/run_step.py --step ingest` (or the pipeline cell); see `docs/orchestration_plan.md`.
- **"schema drift" alert** → diff the incoming schema against the baseline; pin ingest to
  the last known-good version and page the Data owner.
- **"null rate" alert** → check the rolling-window warm-up and the source feed; do not
  impute until the cause is known.
- **"PSI / drift" alert** → re-run `notebooks/eda.ipynb` on recent data; decide retrain
  vs. feature rebuild.
- **"AUC below threshold" alert** → verify label delay (targets need the *next* close),
  then trigger retrain and shadow-test before promotion.
- **"latency / job failure" alert** → check load and the job log; replay from the last
  checkpoint artifact in `data/processed/`.
- **Rollback** → replace `model/model.pkl` with the previous `model_vN.pkl`; requires ML
  owner approval, and the rollback is logged in the issue tracker.

## Ownership summary

Data on-call → freshness / null / schema. ML on-call → drift / AUC / retrain. Platform
on-call → latency / job success. Analyst (weekly) → business hit-rate and the dashboard.
