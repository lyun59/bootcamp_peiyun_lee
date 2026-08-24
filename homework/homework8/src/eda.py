"""Reusable EDA helpers (Stage 08 — Exploratory Data Analysis).

One profiling function for the whole project, instead of ten pasted copies of the
same `.describe()` block in different notebooks.
"""

import pandas as pd


def eda_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a per-column profile: dtype, missingness, cardinality, and (for
    numeric columns) mean / std / min / max.

    Args:
        df: DataFrame to profile.

    Returns:
        A DataFrame with one row per column and one column per statistic.
    """
    rows = []
    for col in df.columns:
        s = df[col]
        row = {
            "dtype": str(s.dtype),
            "n_missing": int(s.isna().sum()),
            "pct_missing": round(float(s.isna().mean()), 4),
            "n_unique": int(s.nunique(dropna=True)),
        }
        if pd.api.types.is_numeric_dtype(s):
            row.update(
                {
                    "mean": round(float(s.mean()), 4),
                    "std": round(float(s.std(ddof=1)), 4),
                    "min": round(float(s.min()), 4),
                    "max": round(float(s.max()), 4),
                }
            )
        rows.append(row)
    return pd.DataFrame(rows, index=df.columns)


def flag_columns(
    df: pd.DataFrame, missing_threshold: float = 0.3, dom_share: float = 0.9
) -> list:
    """Flag columns that may need attention before feature engineering (stage 09).

    Flags columns with (a) missingness above ``missing_threshold``, (b) a single
    value dominating ``dom_share`` of the rows, or (c) zero variance for numeric
    columns.

    Args:
        df: DataFrame to check.
        missing_threshold: Missing fraction above which a column is flagged.
        dom_share: Dominant-category share above which a categorical column is
            flagged as near-constant.

    Returns:
        A list of ``(column, reason)`` tuples; empty if nothing needs attention.
    """
    flags = []
    for col in df.columns:
        s = df[col]
        miss = s.isna().mean()
        if miss > missing_threshold:
            flags.append((col, f"{miss:.1%} missing"))
            continue
        if s.nunique(dropna=True) <= 1:
            flags.append((col, "constant"))
            continue
        if pd.api.types.is_numeric_dtype(s):
            if s.std(ddof=1) == 0:
                flags.append((col, "zero variance"))
        else:
            top_share = s.value_counts(normalize=True, dropna=True).iloc[0]
            if top_share >= dom_share:
                flags.append((col, f"{top_share:.0%} in one category"))
    return flags
