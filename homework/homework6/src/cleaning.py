"""Reusable data-cleaning functions (Stage 06 — Data Preprocessing).

Each function returns a *new* DataFrame rather than mutating the input, so
calls can be chained and the raw data stays untouched for before/after
comparison.
"""

import pandas as pd


def fill_missing_median(df: pd.DataFrame, columns):
    """Fill missing values in numeric columns with the column median.

    Assumption: the median is more robust to outliers than the mean, so it is
    the safer single-value imputation for skewed numeric data (e.g. income).

    Args:
        df: Input DataFrame.
        columns: Iterable of numeric column names to impute.

    Returns:
        A new DataFrame with the given columns' NaNs replaced by their median.
    """
    out = df.copy()
    for col in columns:
        if col in out.columns:
            out[col] = out[col].fillna(out[col].median())
    return out


def drop_missing(df: pd.DataFrame, threshold: float = 0.5):
    """Drop columns whose missing fraction exceeds ``threshold``.

    Assumption: a column with most of its values missing carries too little
    signal to be useful, and imputing that much would be unreliable.

    Args:
        df: Input DataFrame.
        threshold: Missing fraction above which a column is dropped
            (default 0.5, i.e. more than half missing).

    Returns:
        A new DataFrame with high-missing columns removed.
    """
    out = df.copy()
    keep = out.columns[out.isna().mean() <= threshold]
    return out[keep]


def normalize_data(df: pd.DataFrame, columns):
    """Min-max scale numeric columns to the [0, 1] range.

    Assumption: features on different scales (age vs. income) should share a
    common scale before modeling; min-max preserves each distribution's shape
    and keeps values bounded in [0, 1] (alternative: z-score standardization).

    Args:
        df: Input DataFrame.
        columns: Iterable of numeric column names to scale.

    Returns:
        A new DataFrame with the given columns scaled to [0, 1].
    """
    out = df.copy()
    for col in columns:
        if col in out.columns:
            lo = out[col].min()
            hi = out[col].max()
            if hi > lo:
                out[col] = (out[col] - lo) / (hi - lo)
            else:
                out[col] = 0.0  # constant column -> avoid divide-by-zero
    return out
