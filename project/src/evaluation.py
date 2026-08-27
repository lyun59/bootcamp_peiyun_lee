"""Evaluation & risk helpers (Stage 11).

Bootstrap confidence intervals and scenario-comparison utilities for the TSM
next-day direction project. Adapted from the Stage 11 homework, but tuned to the
project's outputs: a classification AUC and a regression RMSE.

Reproducibility is explicit — every bootstrap takes a seed. The core idea is the
same as the homework: resample rows *with replacement* (holding features and label
together) and take percentiles, so the interval reflects sampling uncertainty
without assuming normality.
"""

from __future__ import annotations

from typing import Callable, Dict, Tuple

import numpy as np
from sklearn.metrics import roc_auc_score


def bootstrap_metric(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    fn: Callable[[np.ndarray, np.ndarray], float],
    n_boot: int = 500,
    seed: int = 111,
    alpha: float = 0.05,
) -> Dict[str, float]:
    """Bootstrap a scalar metric by resampling rows (label + prediction together).

    Args:
        y_true: True labels/targets.
        y_pred: Predictions (class labels or scores).
        fn: Metric function taking ``(y_true_subset, y_pred_subset)``.
        n_boot: Number of bootstrap resamples.
        seed: RNG seed for reproducibility.
        alpha: Two-sided tail probability (0.05 => 95% interval).

    Returns:
        ``{"mean": ..., "lo": ..., "hi": ...}`` (percentile interval).
    """
    rng = np.random.default_rng(seed)
    idx = np.arange(len(y_true))
    stats = []
    for _ in range(n_boot):
        b = rng.choice(idx, size=len(idx), replace=True)
        stats.append(fn(y_true[b], y_pred[b]))
    lo, hi = np.percentile(stats, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {"mean": float(np.mean(stats)), "lo": float(lo), "hi": float(hi)}


def bootstrap_auc(
    y_true: np.ndarray,
    y_score: np.ndarray,
    n_boot: int = 500,
    seed: int = 111,
    alpha: float = 0.05,
) -> Dict[str, float]:
    """Bootstrap a 95% confidence interval for AUC.

    Resamples rows (true label + predicted score together) and recomputes AUC each
    time. A robust, non-parametric uncertainty estimate that does not assume the
    AUC is normally distributed.

    Args:
        y_true: Binary labels.
        y_score: Predicted probability of the positive class.
        n_boot, seed, alpha: As in :func:`bootstrap_metric`.

    Returns:
        ``{"mean", "lo", "hi"}`` around the AUC.
    """
    return bootstrap_metric(y_true, y_score, lambda y, s: roc_auc_score(y, s), n_boot, seed, alpha)


def gaussian_interval(
    samples: np.ndarray, alpha: float = 0.05
) -> Tuple[float, float]:
    """A normal-theory 95% interval (mean +/- z * std) from bootstrap samples.

    The "bootstrap normal interval": it assumes the statistic is approximately
    normally distributed, using the spread of the bootstrap distribution as the
    estimate of its standard error. Included as the *optimistic* comparison for the
    percentile interval — under a skewed or fat-tailed statistic the normal band is
    too narrow, which is exactly the assumption the stakeholder should see tested.

    Args:
        samples: The statistic's bootstrap distribution.
        alpha: Two-sided tail probability.

    Returns:
        ``(lo, hi)``.
    """
    from scipy import stats

    z = stats.norm.ppf(1 - alpha / 2)
    mu, sd = float(np.mean(samples)), float(np.std(samples, ddof=1))
    return mu - z * sd, mu + z * sd


def bootstrap_auc_samples(
    y_true: np.ndarray,
    y_score: np.ndarray,
    n_boot: int = 500,
    seed: int = 111,
) -> np.ndarray:
    """Return the full bootstrap distribution of the AUC (for interval comparisons).

    Args:
        y_true: Binary labels.
        y_score: Predicted probability of the positive class.
        n_boot: Number of resamples.
        seed: RNG seed.

    Returns:
        1-D array of ``n_boot`` AUC values.
    """
    rng = np.random.default_rng(seed)
    idx = np.arange(len(y_true))
    out = np.empty(n_boot)
    for i in range(n_boot):
        b = rng.choice(idx, size=len(idx), replace=True)
        out[i] = roc_auc_score(y_true[b], y_score[b])
    return out
