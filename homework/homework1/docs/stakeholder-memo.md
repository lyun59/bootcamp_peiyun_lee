# Stakeholder Brief — Next-Day Direction Forecast for AAPL

**Audience:** Individual investor (decision-maker & end user)
**Cadence:** Daily, after market close
**Decision Supported:** Hold vs. trim a single-stock position

## Context

The investor currently decides each evening whether to hold or trim AAPL based
on gut feel and late-breaking news. This is hard to justify after the fact and
impossible to benchmark. A small, transparent forecast gives the decision a
consistent, measurable basis.

## What You'll Receive

- A daily **up / down** forecast with a confidence score and the top 2–3
  features driving it.
- A directional-accuracy track record against a naive "always up" baseline, so
  you can see whether the model is actually adding value over time.

## Assumptions & Constraints

- Uses free daily OHLCV history (`yfinance`); no real-time feed.
- Does not model transaction costs, fees, or slippage.
- A forecast is a decision aid, not a guarantee; the final decision stays yours.

## Decision Trigger

- Act only when the forecast differs from your prior view and its confidence
  clears a threshold; otherwise hold.
