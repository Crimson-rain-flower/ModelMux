import os

import joblib
from flask import Flask, jsonify, request

app = Flask(__name__)
NAME = os.environ["MODEL"]
model = joblib.load(f"models/{NAME}.joblib")


@app.post("/predict")
def predict():
    p = model.predict_proba([request.json["features"]])[0]
    return jsonify(label=int(p.argmax()), confidence=float(p.max()), model=NAME)


@app.get("/health")
def health():
    return jsonify(status="ok", model=NAME)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
