"""Reusable feature-engineering helpers (Stage 09 — Feature Engineering).

The three features from the lecture, factored into functions so they can be
re-applied to a real (non-synthetic) dataset without copy-pasting the same
arithmetic into every notebook.

All functions return a new Series / DataFrame; none mutate their input except
where the docstring says so.
"""

import pandas as pd


def spend_income_ratio(df: pd.DataFrame, spend_col: str, income_col: str) -> pd.Series:
    """Spending as a fraction of income.

    Args:
        df: DataFrame containing both columns.
        spend_col: Column holding spending.
        income_col: Column holding income.

    Returns:
        A Series of ``spend / income``. On real data, guard against zero income
        first (division by zero yields ``inf``).
    """
    return df[spend_col] / df[income_col]


def disposable_income(df: pd.DataFrame, income_col: str, spend_col: str) -> pd.Series:
    """Income minus spending — the surplus left after monthly spend.

    Captures net capacity to absorb a shock, which raw income alone does not:
    two people with the same income but very different spend have very different
    risk.

    Args:
        df: DataFrame containing both columns.
        income_col: Column holding income.
        spend_col: Column holding spending.

    Returns:
        A Series of ``income - spend``.
    """
    return df[income_col] - df[spend_col]


def encode_region(
    df: pd.DataFrame,
    col: str = "region",
    method: str = "onehot",
    drop_first: bool = True,
) -> pd.DataFrame:
    """Encode a categorical column using one of the three lecture encodings.

    Args:
        df: DataFrame containing the categorical column.
        col: Categorical column to encode.
        method: ``'onehot'``, ``'label'``, or ``'frequency'``.
        drop_first: (onehot only) drop the first dummy column so the remaining
            dummies are not perfectly collinear with an intercept.

    Returns:
        A new DataFrame with the categorical column replaced by its encoding.
    """
    if method == "onehot":
        dummies = pd.get_dummies(df[col], prefix=col, drop_first=drop_first)
        return pd.concat([df.drop(columns=[col]), dummies], axis=1)

    if method == "label":
        out = df.copy()
        out[f"{col}_label"] = pd.factorize(df[col])[0]
        return out.drop(columns=[col])

    if method == "frequency":
        freqs = df[col].value_counts(normalize=True)
        out = df.copy()
        out[f"{col}_freq"] = df[col].map(freqs)
        return out.drop(columns=[col])

    raise ValueError(f"unknown method: {method!r} (use 'onehot', 'label', or 'frequency')")
