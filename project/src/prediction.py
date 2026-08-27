"""Prediction & deployment helpers (Stage 13 — Productization).

This module is the "refactor" that Stage 13 asks for: the model fitting and
prediction logic that used to live inline in the notebooks is moved into reusable
functions here, so the Flask app, the pipeline and any future caller share the same
code path. The model is loaded once and cached, and saved to ``model/model.pkl`` so
a deployed API does not retrain on every startup.
"""

from __future__ import annotations

from typing import Dict, Optional, Union

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import PROJECT_ROOT
from src.modeling import MODEL_FEATURES, load_modeling_data, prepare_features

MODEL_PATH = PROJECT_ROOT / "model" / "model.pkl"


def train_classification_model(X_train: np.ndarray, y_train: np.ndarray) -> Pipeline:
    """Fit the production classification pipeline (StandardScaler -> Logistic).

    Args:
        X_train: Design matrix (rows x features).
        y_train: Binary labels.

    Returns:
        A fitted sklearn ``Pipeline``.
    """
    pipe = Pipeline(
        [("scaler", StandardScaler()), ("logit", LogisticRegression(max_iter=1000))]
    )
    pipe.fit(X_train, y_train)
    return pipe


def save_model(pipe: Pipeline, path: Union[str, object] = MODEL_PATH) -> None:
    """Persist a fitted pipeline with joblib (overwrites any existing file)."""
    from pathlib import Path

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, p)


def load_or_train_model(path: Union[str, object] = MODEL_PATH) -> Pipeline:
    """Return a fitted model, loading from disk or training and saving if absent.

    If ``model/model.pkl`` exists it is loaded (so a deployed app does not retrain);
    otherwise the model is fit on the full featured dataset and saved for next time.

    Args:
        path: Location of the pickled model.

    Returns:
        A fitted ``Pipeline``.
    """
    from pathlib import Path

    p = Path(path)
    if p.exists():
        return joblib.load(p)

    df = load_modeling_data()
    X, _, y_clf = prepare_features(df)
    pipe = train_classification_model(X.values, y_clf.values)
    save_model(pipe, p)
    return pipe


def features_to_array(features: Union[list, Dict[str, float]]) -> np.ndarray:
    """Coerce a prediction input into a (1, n_features) design-matrix row.

    Accepts either a list of numbers in ``MODEL_FEATURES`` order, or a dict keyed by
    feature name (any subset is allowed as long as every model feature is present).

    Args:
        features: List (length = len(MODEL_FEATURES)) or dict of feature values.

    Returns:
        A 2-D numpy array with one row.

    Raises:
        ValueError: If the input is missing features or not numeric.
    """
    if isinstance(features, dict):
        missing = [f for f in MODEL_FEATURES if f not in features]
        if missing:
            raise ValueError(f"missing features: {missing}")
        row = [features[f] for f in MODEL_FEATURES]
    else:
        row = list(features)
        if len(row) != len(MODEL_FEATURES):
            raise ValueError(
                f"expected {len(MODEL_FEATURES)} features, got {len(row)}"
            )
    try:
        arr = np.array(row, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("all features must be numeric") from exc
    return arr.reshape(1, -1)


def predict_direction(
    model: Pipeline, features: Union[list, Dict[str, float]]
) -> Dict:
    """Return the model's next-day direction call for one row of features.

    Args:
        model: A fitted ``Pipeline`` (with ``predict_proba``).
        features: Feature values (list or dict, see :func:`features_to_array`).

    Returns:
        ``{"probability_up", "direction", "direction_label"}``.
    """
    X = features_to_array(features)
    prob_up = float(model.predict_proba(X)[0, 1])
    direction = int(prob_up >= 0.5)
    return {
        "probability_up": prob_up,
        "direction": direction,
        "direction_label": "up" if direction else "down",
    }


def latest_feature_row(df: Optional[object] = None) -> Dict[str, float]:
    """Return the most recent complete feature row as a dict (a live example input).

    Useful for demoing ``/predict`` with real data. Returns a dict keyed by feature
    name, which ``features_to_array`` accepts directly.
    """
    if df is None:
        df = load_modeling_data()
    X, _, _ = prepare_features(df)
    last = X.iloc[-1]
    return {f: float(last[f]) for f in MODEL_FEATURES}
