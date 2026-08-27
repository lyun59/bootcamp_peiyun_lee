"""Flask API for the TSM next-day direction model (Stage 13 — Productization).

Serves the trained logistic-regression classifier behind a JSON API:

* ``GET  /health``               — liveness check.
* ``POST /predict``              — next-day direction call from a feature row.
* ``POST /run_full_analysis``    — re-run both tracks and return headline metrics.

The model is loaded once at startup (from ``model/model.pkl``, trained on first run
if absent). Input validation returns a JSON error and HTTP 400 — never a traceback.

Run with::

    python app.py

The server listens on port 5001 (5000 is occupied by macOS AirPlay Receiver).
"""

from flask import Flask, jsonify, request

from src.prediction import load_or_train_model, predict_direction, features_to_array
from src.modeling import MODEL_FEATURES

# Loaded ONCE at startup, not inside a route.
model = load_or_train_model()
app = Flask(__name__)


def _bad_request(message: str):
    return jsonify({"error": message}), 400


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "n_features": len(MODEL_FEATURES)})


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}
    features = data.get("features")
    if features is None:
        return _bad_request("missing 'features' (list or dict of feature values)")
    try:
        result = predict_direction(model, features)
    except ValueError as exc:
        return _bad_request(str(exc))
    return jsonify(result)


@app.route("/run_full_analysis", methods=["POST"])
def run_full_analysis():
    """Re-run both modeling tracks end-to-end and return headline metrics."""
    from src.modeling import run_all, load_modeling_data

    try:
        df = load_modeling_data()
        res = run_all(df)
    except Exception as exc:  # surface any pipeline error as JSON, not a traceback
        return jsonify({"error": f"analysis failed: {exc}"}), 500

    reg, clf = res["reg"], res["clf"]
    return jsonify(
        {
            "regression": {"rmse": reg["rmse"], "mae": reg["mae"], "r2": reg["r2"]},
            "classification": {
                "accuracy": clf["accuracy"],
                "auc": clf["auc"],
                "precision": clf["precision"],
                "recall": clf["recall"],
            },
            "n_features": len(res["features"]),
        }
    )


if __name__ == "__main__":
    app.run(port=5001)
