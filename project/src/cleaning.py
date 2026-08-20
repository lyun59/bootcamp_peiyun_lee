"""Reusable data-cleaning and preprocessing functions (Stage 06).

Each function returns a *new* DataFrame rather than mutating its input, so steps
can be chained and the raw data stays available for before/after comparison.
"""

import pandas as pd


def fill_missing_median(df: pd.DataFrame, columns) -> pd.DataFrame:
    """Fill missing values in the given columns with their column median.

    Assumption: the median is more robust to outliers than the mean, so it is the
    safer single-value imputation for numeric columns.

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


def drop_missing(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
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


def normalize_data(df: pd.DataFrame, columns) -> pd.DataFrame:
    """Min-max scale the given numeric columns to the [0, 1] range.

    Assumption: features on different scales should share a common scale before
    modeling; min-max keeps values bounded in [0, 1] while preserving shape.

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


def add_features(df: pd.DataFrame, close_col: str = "close") -> pd.DataFrame:
    """Add predictive features and a binary next-day direction target.

    Adds one-day return, rolling means and volatility, and ``target`` = 1 if the
    next day's close is higher than today's (0 otherwise).

    Note: the final row has no next-day close, so its ``target`` is 0 by
    convention (a placeholder — drop it before modeling).

    Args:
        df: Input DataFrame (must contain ``close_col``).
        close_col: Name of the close-price column.

    Returns:
        A new DataFrame with the feature and target columns appended.
    """
    out = df.copy()
    out["return_1d"] = out[close_col].pct_change()
    out["ma_5"] = out[close_col].rolling(5).mean()
    out["ma_20"] = out[close_col].rolling(20).mean()
    out["vol_20"] = out[close_col].rolling(20).std()
    out["target"] = (out[close_col].shift(-1) > out[close_col]).astype(int)
    return out
