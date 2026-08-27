# TSM Next-Day Direction Forecast — Project Summary

*A plain-language summary for a non-technical reader. If you read nothing else, read
this.*

---

## The problem

Every trading day, an investor asks the same question: **will TSM (Taiwan Semiconductor,
one of the world's largest chipmakers) close higher or lower tomorrow than it did today?**
If a simple, explainable rule could answer that even slightly better than a coin flip, it
would be a real edge.

We set out to build that rule using only things we could know by the end of today — the
day's open, high, low, close, and volume, plus a few recent days of history.

## What we did

We ran the full data-science lifecycle, from raw data to a working tool:

1. **Got the data** — pulled six years of daily TSM prices (2020–2025) from Yahoo Finance.
2. **Cleaned and organised it** — stored it reproducibly, documented how we handle
   outliers (the unusual big up/down days).
3. **Explored it** — confirmed the daily moves are noisy, slightly fat-tailed, and hard to
   predict.
4. **Built features** — turned raw prices into ~9 "signals" (momentum, trend position,
   volume surge, overnight gap, and so on), all carefully built so they only use the past.
5. **Trained two models** — one to guess the *size* of tomorrow's move, one to guess its
   *direction* (up or down).
6. **Checked the result rigorously** — measured uncertainty with resampling, and tested
   whether the answer changes if we change our assumptions.
7. **Packaged it** — saved the model, wrapped it in a small web service (`app.py`) that
   returns a prediction, and wrote instructions for anyone who inherits the project.
8. **Planned for production** — wrote down what we would monitor and who would own it, if
   this ever ran for real.

## What we found

**The honest answer is: there is no reliable next-day edge in this data.**

- The direction model is right about **50%** of the time — the same as flipping a coin.
- Its "area under the curve" (a standard quality score, where 0.5 = no skill) is **0.53**,
  and the uncertainty band around that score comfortably includes 0.5.
- The move-size model is also no better than guessing the average.

Crucially, **this is not because we did something wrong.** We tried different models and
different sets of signals, and the answer stayed the same. For a huge, heavily-traded
company like TSM, tomorrow's direction is mostly noise. That is a genuine, useful finding:
it means a simple price-and-volume rule will *not* reliably tell you whether to buy or sell
for the next day.

The one mild, plausible signal we saw: unusually heavy trading volume slightly tilts the
odds toward an up day, and a price stretched far above its 20-day average slightly tilts
toward a down day. Both are too small to trade on.

## What we would not rely on

- **Do not trade on this signal.** It is at chance, and any single good run is noise.
- The result is based on six years of one stock; it may not generalise to other names or
  to a different market regime.
- A big structural change (a crash, a different volatility regime) could make even this
  baseline behave differently.

## What we would do next

1. **Look at longer horizons** — a weekly or monthly direction is more likely to contain a
   real signal than a single day.
2. **Bring in more information** — options-implied volatility, market-wide indices, or
   macroeconomic data.
3. **Change the target** — predicting "a big up move" rather than "any up move" is more
   tradeable and more likely to have signal.
4. **Harden the process** — if any future model does show skill, add walk-forward
   validation and tune the decision threshold before using it for real.

---

**Bottom line:** we built the full pipeline and found, with confidence, that a one-day
directional call on TSM from price and volume alone is no better than chance. The value of
this project is the *rigorous, reusable process* that produced that honest answer — and the
clear roadmap for where a real edge might actually be found.
