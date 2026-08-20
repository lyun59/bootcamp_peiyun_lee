"""Reusable outlier detection and handling functions (Stage 07).

Each function takes a pandas Series and returns either a boolean mask (detect)
or a new Series (handle), so the original data is never mutated.
"""

import pandas as pd


def detect_outliers_iqr(series: pd.Series, k: float = 1.5) -> pd.Series:
    """Flag values outside [Q1 - k*IQR, Q3 + k*IQR].

    The IQR rule is robust to skewed data because it uses the median-centred
    quartiles rather than the mean and standard deviation.

    Args:
        series: Numeric values to test.
        k: IQR multiplier (default 1.5, the conventional "mild outlier" bound).

    Returns:
        A boolean Series (same index as ``series``) that is True for outliers.
    """
    if k <= 0:
        raise ValueError("k must be positive")
    s = series.dropna()
    if s.empty:
        return pd.Series(False, index=series.index)
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr
    mask = (series < lower) | (series > upper)
    return mask.fillna(False)


def detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    """Flag values whose |z-score| exceeds ``threshold``.

    The z-score assumes an approximately normal distribution; it is most useful
    for symmetric data. Uses the sample standard deviation (ddof=1).

    Args:
        series: Numeric values to test.
        threshold: Minimum |z-score| to be flagged (default 3.0).

    Returns:
        A boolean Series (same index as ``series``) that is True for outliers.
    """
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    s = series.dropna()
    if s.empty:
        return pd.Series(False, index=series.index)
    mu = s.mean()
    sigma = s.std(ddof=1)
    if sigma == 0:
        return pd.Series(False, index=series.index)  # constant series, no outliers
    z = (series - mu) / sigma
    mask = z.abs() > threshold
    return mask.fillna(False)


def winsorize_series(series: pd.Series, lower: float = 0.05, upper: float = 0.95) -> pd.Series:
    """Clip values to the [``lower``, ``upper``] quantiles (winsorize).

    Unlike dropping outliers, winsorizing keeps every row but caps extreme
    values, which is useful when the sample is small or every row matters.

    Args:
        series: Numeric values to clip.
        lower: Lower quantile to clip at (default 0.05).
        upper: Upper quantile to clip at (default 0.95).

    Returns:
        A new Series with extreme values capped at the quantile bounds.
    """
    if not (0 <= lower < upper <= 1):
        raise ValueError("need 0 <= lower < upper <= 1")
    lo = series.quantile(lower)
    hi = series.quantile(upper)
    return series.clip(lower=lo, upper=hi)
