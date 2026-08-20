# Stakeholder Memo — TSM Next-Day Direction Signal

**To:** Project lead
**From:** Data team
**Re:** One-day TSM direction forecast

## What we are solving

We are building a binary signal — up or down for TSM's next trading close — from
historical price and volume features only. The deliverable is a reproducible
pipeline (acquisition → storage → preprocessing → outlier handling) that ends in a
documented, explainable directional call.

## Who it serves

A retail investor / junior analyst needs a daily, explainable directional call.
They value **actionability**, **explainability**, and **reproducibility** over raw
forecast accuracy.

## Scope

- **In scope:** daily OHLCV features, a documented preprocessing + outlier pipeline,
  and a reproducible acquisition → storage → preprocessing flow.
- **Out of scope:** intraday data, fundamentals or options data, portfolio sizing,
  and execution/trade timing.

## Risks & assumptions

- Past price patterns do not guarantee future direction; the signal is
  probabilistic and should be treated as one input among many.
- Market data can be revised after the fact; we pin the acquisition date and the
  date range for reproducibility and document any assumptions about data quality.
