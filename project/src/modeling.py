"""Modeling helpers for the TSM next-day direction project (Stages 10a & 10b).

The project goal is binary classification (will TSM close up or down tomorrow),
but the lifecycle asks for both a regression baseline (predicting the *size* of
tomorrow's move) and the classification model (predicting its *direction*).
Both live here behind one small, reusable API so the notebook, the pipeline and
the Flask app all share the same feature list and split logic.

Design decisions (documented here because they travel with the results):

* **Leakage-safe targets.** Features use only information known by today's close;
  the regression target is tomorrow's return ``return_1d.shift(-1)`` and the
  classification target is ``target`` (already ``close.shift(-1) > close``).
  Nothing looks at the future except the label itself.

* **Time-aware split.** Daily returns are serially correlated, so a random split
  would leak tomorrow's information into "past" training rows. We always split on
  time (first 80% train, last 20% test) and never shuffle.

* **Stationary feature subset.** Raw ``ma_5``/``ma_20``/``vol_20`` are price-scaled
  and trend with the multi-year price rise (TSM roughly tripled over the sample),
  so they are excluded from ``MODEL_FEATURES``. The ratio/return features that
  remain are unit-free and roughly stationary, which is what a linear/logistic
  model can use safely without leaking the price level.
"""

from __future__ import annotations

from typing import Dict, Iterable, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import DATA_DIR_PROCESSED, TICKER

# Stationary, unit-free predictors (see module docstring for why ma_5/ma_20/vol_20
# are left out). Sorted for stable, reproducible ordering.
MODEL_FEATURES = [
    "return_1d",
    "return_5d",
    "return_20d",
    "close_to_ma_5",
    "close_to_ma_20",
    "ma_5_20_spread",
    "volume_ratio_20",
    "intraday_range",
    "overnight_gap",
]

TRAIN_FRAC = 0.8
RANDOM_STATE = 42


def load_modeling_data(path: Optional[str] = None) -> pd.DataFrame:
    """Load the featured dataset and return it with a clean, sorted date index.

    Args:
        path: Override path to the featured CSV (defaults to the env-driven path).

    Returns:
        DataFrame indexed by ``Date`` (sorted), with all feature columns.
    """
    p = path or (DATA_DIR_PROCESSED / f"{TICKER.lower()}_featured.csv")
    df = pd.read_csv(p, parse_dates=["Date"])
    df = df.sort_values("Date").set_index("Date")
    return df


def prepare_features(
    df: pd.DataFrame, features: Optional[Iterable[str]] = None
) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Split ``df`` into design matrix X and the two targets.

    Rows with any missing feature (the rolling warm-up at the start of the series)
    are dropped. The final row has no next-day close, so its regression target is
    NaN and is dropped too.

    Args:
        df: Featured DataFrame (as returned by :func:`load_modeling_data`).
        features: Feature columns to use (default ``MODEL_FEATURES``).

    Returns:
        ``(X, y_reg, y_clf)`` — design matrix, next-day return, next-day direction.
    """
    cols = list(features) if features is not None else MODEL_FEATURES
    X = df[cols].copy()
    y_reg = df["return_1d"].shift(-1)          # tomorrow's return
    y_clf = df["target"]                        # already tomorrow's direction
    mask = X.notna().all(axis=1) & y_reg.notna()
    return X.loc[mask], y_reg.loc[mask], y_clf.loc[mask]


def time_aware_split(
    X: pd.DataFrame, y: pd.Series, train_frac: float = TRAIN_FRAC
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Chronological train/test split (no shuffle).

    Args:
        X: Design matrix (rows already sorted by time).
        y: Target aligned with ``X``.
        train_frac: Fraction of rows for training (default 0.8).

    Returns:
        ``(X_train, X_test, y_train, y_test)`` as numpy arrays.
    """
    cut = int(len(X) * train_frac)
    return X.iloc[:cut].values, X.iloc[cut:].values, y.iloc[:cut].values, y.iloc[cut:].values


def run_linear_regression(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    feature_names: Optional[Iterable[str]] = None,
) -> Dict:
    """Fit a scaled linear regression and return metrics, residuals and the model.

    Args:
        X_train/X_test: Design matrices (numpy arrays, already scaled later).
        y_train/y_test: Regression targets.
        feature_names: Column names for ``X`` (default ``MODEL_FEATURES``); used
            only to label the coefficient table.

    Returns:
        A dict with keys: ``model``, ``y_pred``, ``residuals``, ``rmse``, ``mae``,
        ``r2``, ``baseline_rmse`` (naive mean forecast on the test set), and
        ``coefs`` (DataFrame of standardized coefficients).
    """
    names = list(feature_names) if feature_names is not None else MODEL_FEATURES
    pipe = Pipeline([("scaler", StandardScaler()), ("reg", LinearRegression())])
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    resid = y_test - y_pred

    # Standardized coefficients = effect of a 1-std move in each feature.
    scaler = pipe.named_steps["scaler"]
    reg = pipe.named_steps["reg"]
    std_coefs = reg.coef_ * scaler.scale_
    coefs = pd.DataFrame(
        {"feature": names, "std_coef": std_coefs}
    ).sort_values("std_coef", key=abs, ascending=False)

    return {
        "model": pipe,
        "y_pred": y_pred,
        "residuals": resid,
        "rmse": float(mean_squared_error(y_test, y_pred) ** 0.5),
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "r2": float(r2_score(y_test, y_pred)),
        "baseline_rmse": float(np.std(y_test, ddof=1)),
        "coefs": coefs,
    }


def run_logistic_classification(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    feature_names: Optional[Iterable[str]] = None,
) -> Dict:
    """Fit a scaled logistic regression and return metrics, probabilities, model.

    Args:
        X_train/X_test: Design matrices.
        y_train/y_test: Binary targets.
        feature_names: Column names for ``X`` (default ``MODEL_FEATURES``).

    Returns:
        A dict with keys: ``model``, ``y_pred``, ``y_prob``, ``accuracy``,
        ``precision``, ``recall``, ``f1``, ``auc``, ``confusion`` (np.ndarray),
        ``baseline_accuracy`` (majority class on the test set), ``coefs``.
    """
    names = list(feature_names) if feature_names is not None else MODEL_FEATURES
    pipe = Pipeline(
        [("scaler", StandardScaler()), ("logit", LogisticRegression(max_iter=1000))]
    )
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    y_prob = pipe.predict_proba(X_test)[:, 1]

    scaler = pipe.named_steps["scaler"]
    logit = pipe.named_steps["logit"]
    std_coefs = logit.coef_[0] * scaler.scale_
    coefs = pd.DataFrame(
        {"feature": names, "std_coef": std_coefs}
    ).sort_values("std_coef", key=abs, ascending=False)

    return {
        "model": pipe,
        "y_pred": y_pred,
        "y_prob": y_prob,
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "auc": float(roc_auc_score(y_test, y_prob)),
        "confusion": confusion_matrix(y_test, y_pred),
        "baseline_accuracy": float(max(np.mean(y_test == 1), np.mean(y_test == 0))),
        "coefs": coefs,
    }


def run_all(df: pd.DataFrame, features: Optional[Iterable[str]] = None) -> Dict:
    """One call that loads features, splits, and runs both tracks.

    Convenience for the pipeline and the Flask app, so the exact same steps run
    in the notebook and in production.
    """
    X, y_reg, y_clf = prepare_features(df, features)
    names = list(X.columns)
    X_train, X_test, y_reg_train, y_reg_test = time_aware_split(X, y_reg)
    _, _, y_clf_train, y_clf_test = time_aware_split(X, y_clf)
    reg = run_linear_regression(X_train, y_reg_train, X_test, y_reg_test, names)
    clf = run_logistic_classification(X_train, y_clf_train, X_test, y_clf_test, names)
    return {"reg": reg, "clf": clf, "features": names}
