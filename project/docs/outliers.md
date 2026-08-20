# Outlier Assumptions — TSM Project (Stage 07)

## Definition

Outliers are identified on the **daily simple returns** (`return_1d`), the main
modeling signal, using two rules implemented in `src/outliers.py`:

- **IQR rule** (`detect_outliers_iqr`, k = 1.5): a return is flagged if it falls
  outside `[Q1 − 1.5·IQR, Q3 + 1.5·IQR]`. Robust to skew because it uses
  median-centred quartiles.
- **z-score rule** (`detect_outliers_zscore`, threshold = 3.0): a return is
  flagged if `|z| > 3`, i.e. more than 3 sample standard deviations from the
  mean. Assumes an approximately normal distribution.

## Results (TSM, 2020-01-01 → 2025-12-31)

| Method | Flagged | Share |
|--------|---------|-------|
| IQR (k = 1.5) | 52 | 3.45% |
| z-score (|z| > 3) | 17 | 1.13% |

## Assumptions & risks

- The two rules disagree (3.45% vs 1.13%) because daily returns are **fat-tailed
  and slightly skewed**; the z-score under-reports extreme moves under
  non-normality.
- **Removing** outliers (IQR filtering) discards real extreme moves — for example
  earnings or macro shocks — which may be the most informative days for a
  direction signal.
- **Winsorizing** caps extremes while keeping every row, so it is preferred when
  the sample is small or every trading day matters.

## Decision

For this project we **flag with the IQR rule** (for sensitivity reporting) and,
where handling is required, **winsorize at the 5%/95% quantiles** rather than
drop, so no trading day is lost. This keeps later modeling and reporting on
documented assumptions.
