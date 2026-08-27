# Stakeholder Handoff Summary — TSM Next-Day Direction Forecast

## Overview & purpose

This project asks whether Taiwan Semiconductor (TSM, NYSE ADR) will close **up or down**
tomorrow, using only prior price and volume data. It was built end-to-end through the
full data-science lifecycle — from raw acquisition to a served model — with the explicit
goal of being reproducible, explainable, and honest about uncertainty.

## Key findings & recommendations

- **There is no reliable next-day directional edge in this data.** The classifier scores
  at chance: accuracy ~50% (vs. a 52% majority-class baseline) and AUC 0.53 (95% bootstrap
  CI 0.46–0.59, straddling the 0.5 no-skill line).
- **The result is robust**, not an artefact of one modelling choice: a random forest and a
  momentum-only feature set both score at chance.
- **Recommendation:** do not trade on this signal. Use it as a documented baseline that
  explains *why* a simple price/volume model cannot predict next-day direction, and direct
  future effort toward longer horizons, a richer feature universe, or a different target.

## Assumptions & limitations

- Features use only information known by today's close; the split is chronological
  (no leakage).
- Features are stationary ratios/returns; price-scaled `ma_5/ma_20/vol_20` were excluded.
- The relationship is assumed stable across 2020–2025; a regime shift would invalidate it.
- The decision threshold is 0.5 with symmetric up/down costs.
- The test window is ~300 days, so all metrics are noisy (quantified via bootstrap CIs).

## Risks & potential issues

- The model's near-chance performance means any apparent signal in a single run is noise.
- Market data can be revised after the fact; the acquisition date and range are pinned for
  reproducibility.
- If ever productionised, the model needs monitoring (feature drift, rolling AUC, data
  freshness) — see `docs/monitoring_plan.md`.

## How to use the deliverables

1. **Install** — `pip install -r requirements.txt`, copy `.env.example` to `.env`.
2. **Reproduce end-to-end** — run `notebooks/project_pipeline.ipynb` top to bottom.
3. **Explore** — `notebooks/eda.ipynb`, `modeling_regression.ipynb`,
   `modeling_classification.ipynb`, `evaluation.ipynb`, `productization.ipynb`.
4. **Serve the model** — `python app.py`, then call the API (see README for examples).
5. **Read the findings** — `reports/final_report.md` (decision-oriented) and this document.

## Suggested next steps

1. Try longer-horizon targets (weekly/monthly) where a signal is more likely to exist.
2. Add a richer feature universe (options-implied volatility, macro, cross-asset).
3. Reframe the target (e.g. "large up move" instead of "any up") for a more tradeable edge.
4. Add walk-forward validation and decision-threshold calibration before any live use.
