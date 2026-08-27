"""CLI wrapper for the "train" pipeline task (Stage 15 — Orchestration).

Refactors the model-fitting step out of the notebook into a reusable function that
runs from the command line with simple logging and a checkpoint (the saved model).

Run from the project root::

    python src/run_step.py --step train

This reproduces what ``notebooks/productization.ipynb`` does in its "Persist the
model" cell — fit the classification pipeline on the full featured dataset and
write ``model/model.pkl`` — but headless, so it can be scheduled.

Idempotency: yes. Re-running overwrites ``model/model.pkl`` with a model fit on the
same data and (because logistic regression is deterministic) identical parameters,
so the output is the same on every run.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Allow `python src/run_step.py` to resolve the `src` package imports.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.modeling import load_modeling_data, prepare_features, MODEL_FEATURES  # noqa: E402
from src.prediction import save_model, train_classification_model, MODEL_PATH  # noqa: E402

log = logging.getLogger("run_step")


def train_step() -> int:
    """Fit the classification model on the full dataset and save it. Returns 0 on success."""
    log.info("[train] start")
    df = load_modeling_data()
    X, _, y_clf = prepare_features(df)
    log.info("[train] loaded %d rows x %d features", len(X), len(MODEL_FEATURES))

    model = train_classification_model(X.values, y_clf.values)
    save_model(model, MODEL_PATH)
    log.info("[train] wrote model -> %s", MODEL_PATH)
    log.info("[train] done (idempotent: same data => same parameters)")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="TSM pipeline step runner")
    parser.add_argument("--step", choices=["train"], default="train",
                        help="which pipeline task to run")
    parser.add_argument("--log-level", default="INFO",
                        help="logging level (DEBUG/INFO/WARNING)")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.step == "train":
        return train_step()
    log.error("unknown step: %s", args.step)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
