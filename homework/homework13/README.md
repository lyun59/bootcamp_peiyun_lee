# Stage 13 Homework - Prediction API

A minimal Flask service that serves a scikit-learn linear-regression model. The model
was trained on a synthetic two-feature regression dataset; the API takes two numeric
features and returns one scalar prediction.

## Running it

    python app.py

The server starts on http://127.0.0.1:5001 and loads model/model.pkl at startup.
(Port 5001 is used because macOS AirPlay Receiver already occupies port 5000.)

## POST /predict

    curl -X POST http://127.0.0.1:5001/predict -H "Content-Type: application/json" -d '{"features": [0.1, 0.2]}'

Response:

    {"prediction": 23.58961171297329}

## GET /predict/<f1>/<f2>

    curl http://127.0.0.1:5001/predict/0.1/0.2

Response:

    {"prediction": 23.58961171297329}

## Bad input

- POST with missing or malformed `features` -> HTTP 400, `{"error": "features must be a list of exactly 2 numbers"}`
- GET with a non-numeric value -> HTTP 400, `{"error": "path values must be numbers"}`

Both return a JSON error and an HTTP 400 status, never a server traceback.
