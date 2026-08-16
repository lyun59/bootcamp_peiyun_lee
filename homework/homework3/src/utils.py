"""Reusable utility functions for the Stage 03 homework.

These helpers are imported from the homework notebook so common data
operations stay in one place instead of being copy-pasted.
"""

import pandas as pd


def get_summary_stats(df: pd.DataFrame, groupby_col: str = "category") -> pd.DataFrame:
    """Return per-category summary statistics for a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset that contains ``groupby_col`` plus one or more numeric
        columns.
    groupby_col : str, optional
        Column used to group the data (default ``"category"``).

    Returns
    -------
    pd.DataFrame
        The mean of each numeric column, aggregated by ``groupby_col``, with
        the group key restored as a regular column.

    Example
    -------
    >>> get_summary_stats(df)
      category     value
    0        A  11.500000
    1        B  15.666667
    2        C  27.666667
    """
    return (
        df.groupby(groupby_col)
        .mean(numeric_only=True)
        .reset_index()
    )
