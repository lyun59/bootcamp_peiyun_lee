
from flask import Flask, request, jsonify
import joblib

# loaded ONCE, at startup - not inside a route
model = joblib.load('model/model.pkl')
app = Flask(__name__)


@app.route('/predict', methods=['POST'])
def predict_post():
    data = request.get_json(silent=True) or {}
    features = data.get('features')
    # TODO 1: validate the payload - must be a list of exactly 2 numbers
    if not isinstance(features, list) or len(features) != 2:
        return jsonify({'error': 'features must be a list of exactly 2 numbers'}), 400
    try:
        # TODO 2: model.predict takes a LIST of rows, so wrap the feature list
        prediction = float(model.predict([features])[0])
    except (ValueError, TypeError):
        return jsonify({'error': 'features must be numbers'}), 400
    return jsonify({'prediction': prediction})


@app.route('/predict/<f1>/<f2>', methods=['GET'])
def predict_get(f1, f2):
    # TODO 3: f1 and f2 arrive as STRINGS; convert to float and 400 on bad input
    try:
        features = [float(f1), float(f2)]
    except ValueError:
        return jsonify({'error': 'path values must be numbers'}), 400
    prediction = float(model.predict([features])[0])
    return jsonify({'prediction': prediction})


if __name__ == '__main__':
    app.run(port=5001)
