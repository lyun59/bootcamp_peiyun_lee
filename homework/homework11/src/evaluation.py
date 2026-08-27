"""Evaluation & risk helpers (Stage 11).

Bootstrap confidence intervals, imputation strategies, a minimal OLS model, and
metric helpers used by the evaluation notebook. Kept dependency-light
(numpy only) and reproducible via explicit seeds.
"""

import numpy as np


def mean_impute(a: np.ndarray) -> np.ndarray:
    """Replace NaNs with the column mean."""
    m = np.nanmean(a)
    out = a.copy()
    out[np.isnan(out)] = m
    return out


def median_impute(a: np.ndarray) -> np.ndarray:
    """Replace NaNs with the column median."""
    m = np.nanmedian(a)
    out = a.copy()
    out[np.isnan(out)] = m
    return out


class SimpleLinReg:
    """Minimal ordinary least squares (y ~ x) fit via the normal equations."""

    def fit(self, X, y):
        X1 = np.c_[np.ones(len(X)), X.ravel()]
        beta = np.linalg.pinv(X1) @ y
        self.intercept_, self.coef_ = float(beta[0]), np.array([float(beta[1])])
        return self

    def predict(self, X):
        return self.intercept_ + self.coef_[0] * X.ravel()


def mae(y_true, y_pred):
    """Mean absolute error."""
    return float(np.mean(np.abs(y_true - y_pred)))


def bootstrap_metric(y_true, y_pred, fn, n_boot=500, seed=111, alpha=0.05):
    """Bootstrap a metric: resample rows with replacement and take percentiles."""
    rng = np.random.default_rng(seed)
    idx = np.arange(len(y_true))
    stats = []
    for _ in range(n_boot):
        b = rng.choice(idx, size=len(idx), replace=True)
        stats.append(fn(y_true[b], y_pred[b]))
    lo, hi = np.percentile(stats, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {"mean": float(np.mean(stats)), "lo": float(lo), "hi": float(hi)}


def bootstrap_predictions(X, y, x_grid, n_boot=500, seed=111):
    """Bootstrap the *fitted line*: refit on each resample and take percentiles."""
    rng = np.random.default_rng(seed)
    preds = []
    idx = np.arange(len(y))
    for _ in range(n_boot):
        b = rng.choice(idx, size=len(idx), replace=True)
        m = SimpleLinReg().fit(X[b].reshape(-1, 1), y[b])
        preds.append(m.predict(x_grid))
    P = np.vstack(preds)
    return P.mean(axis=0), np.percentile(P, 2.5, axis=0), np.percentile(P, 97.5, axis=0)


def fit_fn(X, y):
    return SimpleLinReg().fit(X, y)


def pred_fn(model, X):
    return model.predict(X)
