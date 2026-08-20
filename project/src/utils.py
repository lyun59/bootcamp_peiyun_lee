"""Reusable utility functions (Stage 03 — Python Fundamentals).

Small, documented helpers that later stages import. Each function returns a new
object rather than mutating its input, so calls can be chained and the raw data
stays untouched.
"""

from typing import Optional

import pandas as pd


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Lower-case column names and replace spaces with underscores.

    Example: ``'Adj Close'`` -> ``'adj_close'``. Returns a new DataFrame.
    """
    out = df.copy()
    out.columns = [str(c).strip().lower().replace(" ", "_") for c in out.columns]
    return out


def ensure_datetime_index(df: pd.DataFrame, col: Optional[str] = None) -> pd.DataFrame:
    """Return a copy of ``df`` with a sorted ``DatetimeIndex``.

    If ``col`` is given, that column is parsed to datetime and set as the index;
    otherwise the existing index is converted. Rows are sorted chronologically.
    """
    out = df.copy()
    if col is not None:
        out[col] = pd.to_datetime(out[col])
        out = out.set_index(col)
    out.index = pd.to_datetime(out.index)
    return out.sort_index()


def add_returns(df: pd.DataFrame, close_col: str = "close") -> pd.DataFrame:
    """Add a daily simple-return column ``return`` derived from ``close_col``.

    ``return = close.pct_change()``. The first row is NaN (no prior close).
    Returns a new DataFrame.
    """
    out = df.copy()
    out["return"] = out[close_col].pct_change()
    return out
