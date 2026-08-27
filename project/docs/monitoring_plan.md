# Monitoring Plan — TSM Next-Day Direction Model

If the stage-13 API were deployed, these are the risks it would face and what we would
watch. All thresholds are starting points for a daily-batch service.

## Failure modes & metrics (four layers)

| Layer | Failure mode | Metric | Starting threshold | Alert to | First runbook step |
| --- | --- | --- | --- | --- | --- |
| Data | Market feed delayed / stale | Data freshness | `age_of_latest_row > 26h` | Data on-call | Check the yfinance/feed job and rerun the ingest |
| Data | Schema change or new columns | Schema hash | hash != baseline | Data on-call | Diff the schema; pin the ingest to the last known-good version |
| Data | Missingness rising | Null rate on features | `> 2%` of rows | Data on-call | Inspect the source feed; verify warm-up logic |
| Model | Feature drift | PSI on `volume_ratio_20` / returns | `PSI > 0.20` | ML on-call | Re-run EDA; decide retrain vs. feature rebuild |
| Model | Performance decay | Rolling 20-day AUC | `< 0.45` for 10 consecutive days | ML on-call | Check label delay; trigger retrain and shadow-test |
| System | Slow responses | p95 latency | `> 250 ms` | Platform on-call | Check load / restart worker; scale if persistent |
| System | Job failures | Daily job success rate | `< 99%` over 7 days | Platform on-call | Read the job log; replay from last checkpoint |
| Business | Call no better than chance | 30-day direction hit-rate vs. majority | `hit-rate < majority baseline` | Analyst (weekly) | Escalate to model review; re-evaluate whether to keep serving |

## Retraining cadence & triggers

- **Scheduled:** retrain monthly on a rolling window of recent data.
- **Triggered:** retrain immediately if PSI > 0.20 on a key feature, or rolling 20-day
  AUC < 0.45 for 10 consecutive days, or a schema change alters the feature set.
- Every retrain runs **shadow mode** (logged predictions alongside production) for one
  week before promotion.

## Ownership

- **Analyst (weekly):** reviews the business KPI and the dashboard.
- **Data on-call:** owns ingest freshness, null rate, and schema.
- **ML on-call:** owns PSI, rolling AUC, and the retrain decision.
- **Platform on-call:** owns latency and job success.
- **Rollback approval:** the ML owner approves any model rollback or feature change.
- **Issue log:** all incidents are logged in the repo's issue tracker with the metric,
  threshold, and the runbook step taken.
