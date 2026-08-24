"""Feature engineering for the TSM next-day direction model (Stage 09).

Each function returns a *new* DataFrame, so features can be added without
mutating the source and the raw/cleaned data stays available.

These are the Stage 09 homework feature functions (ratio / difference /
transform ideas) adapted from the credit-demo dataset to price-and-volume data:
instead of a spend-to-income ratio or a categorical encoding, we build momentum,
trend-position, volatility, volume and price-range features — each motivated by
the Stage 08 EDA findings. Rationales are in the docstrings and the README
feature table.
"""

import pandas as pd


def momentum(df: pd.DataFrame, close_col: str = "close", periods=(5, 20)) -> pd.DataFrame:
    """Add price momentum over multiple horizons as pct-change returns.

    ``return_1d`` already exists from Stage 06; these longer horizons capture
    whether a trend is in place. Short and long momentum can disagree, and their
    combination is more informative than either alone.

    Args:
        df: DataFrame containing ``close_col``.
        close_col: Close-price column name.
        periods: Iterable of horizons (in days) to compute returns over.

    Returns:
        A new DataFrame with a ``return_{n}d`` column per horizon.
    """
    out = df.copy()
    for p in periods:
        out[f"return_{p}d"] = out[close_col].pct_change(p)
    return out


def price_to_ma(df: pd.DataFrame, close_col: str = "close", windows=(5, 20)) -> pd.DataFrame:
    """Add close price as a fraction of its rolling mean (trend position).

    A value > 0 means price is above its own recent average (up-trend), < 0 below
    (down-trend). Dividing by the moving average normalises the signal so it stays
    comparable even as the price level rises over the sample.

    Args:
        df: DataFrame containing ``close_col``.
        close_col: Close-price column name.
        windows: Iterable of rolling windows.

    Returns:
        A new DataFrame with a ``close_to_ma_{w}`` column per window.
    """
    out = df.copy()
    for w in windows:
        ma = out[close_col].rolling(w).mean()
        out[f"close_to_ma_{w}"] = out[close_col] / ma - 1.0
    return out


def ma_spread(df: pd.DataFrame, close_col: str = "close", short: int = 5, long: int = 20) -> pd.DataFrame:
    """Add the short-vs-long moving-average spread (a trend-following signal).

    Positive when the fast average is above the slow one (bullish), negative
    otherwise. This is the classic crossover feature; scaling by the long average
    keeps its magnitude stable across the multi-year price rise.

    Args:
        df: DataFrame containing ``close_col``.
        close_col: Close-price column name.
        short: Fast window (default 5).
        long: Slow window (default 20).

    Returns:
        A new DataFrame with a ``ma_{short}_{long}_spread`` column.
    """
    out = df.copy()
    ma_s = out[close_col].rolling(short).mean()
    ma_l = out[close_col].rolling(long).mean()
    out[f"ma_{short}_{long}_spread"] = (ma_s - ma_l) / ma_l
    return out


def volume_surge(df: pd.DataFrame, volume_col: str = "volume", window: int = 20) -> pd.DataFrame:
    """Add volume relative to its rolling mean (activity surge).

    A value > 1 means today's volume is above its recent norm. Unusually high
    volume often accompanies strong directional moves or reversals, so it can
    sharpen a direction signal.

    Args:
        df: DataFrame containing ``volume_col``.
        volume_col: Volume column name.
        window: Rolling window for the baseline mean.

    Returns:
        A new DataFrame with a ``{volume_col}_ratio_{window}`` column.
    """
    out = df.copy()
    vol_mean = out[volume_col].rolling(window).mean()
    out[f"{volume_col}_ratio_{window}"] = out[volume_col] / vol_mean
    return out


def intraday_range(df: pd.DataFrame, high_col: str = "high", low_col: str = "low", close_col: str = "close") -> pd.DataFrame:
    """Add the intraday range (high − low) as a fraction of close.

    A same-day volatility proxy that, unlike the rolling std of returns, is
    available at the end of the day it describes (no warm-up window).

    Args:
        df: DataFrame containing the price columns.
        high_col, low_col, close_col: Column names.

    Returns:
        A new DataFrame with an ``intraday_range`` column.
    """
    out = df.copy()
    out["intraday_range"] = (out[high_col] - out[low_col]) / out[close_col]
    return out


def overnight_gap(df: pd.DataFrame, open_col: str = "open", close_col: str = "close") -> pd.DataFrame:
    """Add the overnight gap: (open − previous close) / previous close.

    Captures news that lands while the market is closed and sets the tone for the
    next session, which the Stage 08 time-series plot shows can be a large
    fraction of daily movement.

    Args:
        df: DataFrame containing the price columns.
        open_col, close_col: Column names.

    Returns:
        A new DataFrame with an ``overnight_gap`` column.
    """
    out = df.copy()
    out["overnight_gap"] = out[open_col] / out[close_col].shift(1) - 1.0
    return out


def build_features(df: pd.DataFrame, close_col: str = "close") -> pd.DataFrame:
    """Apply every feature builder and return a new DataFrame.

    This is the single entry point the pipeline (and the Stage 09 notebook cell)
    calls; individual functions remain importable for reuse.

    Args:
        df: Cleaned OHLCV DataFrame (columns ``open``/``high``/``low``/
            ``close``/``volume``).
        close_col: Close-price column name.

    Returns:
        A new DataFrame with all engineered feature columns appended.
    """
    out = df.copy()
    out = momentum(out, close_col=close_col)
    out = price_to_ma(out, close_col=close_col)
    out = ma_spread(out, close_col=close_col)
    out = volume_surge(out)
    out = intraday_range(out)
    out = overnight_gap(out)
    return out
