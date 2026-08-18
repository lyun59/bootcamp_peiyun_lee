# Next-Day Stock Direction Forecast for AAPL

**Stage:** Problem Framing & Scoping (Stage 01)

## Problem Statement

An individual retail investor reviews a single large-cap stock (AAPL) each
evening after market close and must decide whether to **hold** the position or
**trim** it the next trading day. Today that decision is made from gut feel and
whatever news happens to be at hand, so it is inconsistent, hard to justify
after the fact, and impossible to measure against any benchmark.

This project frames a small, reproducible pipeline that ingests daily price
history, engineers a handful of transparent features, and produces a
next-day **up / down** forecast for the stock. Success is defined by a
measurable criterion: the model's *directional accuracy* on a held-out test
window must beat a naive "always up" baseline (the majority class), and every
forecast must come with a plain-language explanation of what drove it.

## Stakeholder & User

- **Stakeholder (decides):** the individual investor — the same person who will
  act on the signal by holding or trimming. They need a decision aid, not a
  black-box guarantee.
- **User (consumes the output):** also the investor, reviewing a short daily
  report after market close. Cadence: **daily, end-of-day**, so latency is not
  a constraint (no real-time requirement).

## Useful Answer & Decision

- **Type:** *Predictive* (binary classification — price up vs. down next day).
- **Metric:** directional accuracy, plus precision/recall on the "up" class,
  benchmarked against the naive baseline.
- **Artifact:** a one-page daily forecast (signal + confidence + top drivers),
  so the investor sees *why* before acting.

## Assumptions & Constraints

- Daily OHLCV history is available for free via `yfinance` (rate-limited).
- Past price patterns carry some signal for the next day (weak stationarity).
- Transaction costs, fees, and slippage are **not** modeled at this stage.
- Daily cadence only — no intraday or real-time decisioning.

## Known Unknowns / Risks

- Markets are non-stationary; a regime shift can invalidate a trained model.
- Risk of data snooping / overfitting on a single ticker's history.
- The "always up" baseline is genuinely hard to beat in an up-trending market.

## Lifecycle Mapping

- Predict next-day direction → **Problem Framing & Scoping (Stage 01)** → this scoping doc + stakeholder memo
- → Tooling Setup (Stage 02) → project scaffold + env
- → Data Acquisition (Stage 04) → price history into `data/raw/`
- → Data Storage (Stage 05) → processed parquet into `data/processed/`
- → Preprocessing (Stage 06) → clean features
- → Modeling → trained classifier + daily forecast artifact

## Repo Plan

`data/raw/`, `data/processed/`, `src/`, `notebooks/`, `docs/`, `reports/`
