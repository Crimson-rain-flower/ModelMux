import os
import time

import requests
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)
TIERS = ["light", "mid", "heavy"]
COST = {"light": 1, "mid": 4, "heavy": 10}
THRESHOLD = float(os.getenv("THRESHOLD", "0.9"))
HERE = os.path.dirname(os.path.abspath(__file__))
stats = {"requests": 0, "total_cost": 0, "degraded": 0,
         "by_model": {t: 0 for t in TIERS}}


def call(tier, feats):
    r = requests.post(f"http://model-{tier}:5000/predict",
                      json={"features": feats}, timeout=2)
    r.raise_for_status()
    return r.json()


@app.post("/predict")
def predict():
    t0 = time.time()
    feats = request.json["features"]
    priority = request.json.get("priority", False)
    threshold = float(request.json.get("threshold", THRESHOLD))
    order = ["heavy", "mid", "light"] if priority else TIERS

    best, cost, degraded = None, 0, False
    for tier in order:
        try:
            res = call(tier, feats)
        except Exception:
            degraded = True
            continue
        cost += COST[tier]
        best = res
        if priority or res["confidence"] >= threshold:
            break

    if best is None:
        return jsonify(error="all models unavailable"), 503

    stats["requests"] += 1
    stats["total_cost"] += cost
    stats["by_model"][best["model"]] += 1
    stats["degraded"] += int(degraded)
    best.update(cost=cost, degraded=degraded,
                latency_ms=round((time.time() - t0) * 1000, 2))
    return jsonify(best)


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/metrics")
def metrics():
    return jsonify(stats)


@app.get("/")
def index():
    return send_from_directory(HERE, "index.html")


@app.get("/samples")
def samples():
    return send_from_directory(HERE, "samples.json")


@app.get("/status")
def status():
    out = {}
    for t in TIERS:
        try:
            out[t] = requests.get(f"http://model-{t}:5000/health", timeout=1).ok
        except Exception:
            out[t] = False
    return jsonify(out)


@app.post("/reset")
def reset():
    stats.update(requests=0, total_cost=0, degraded=0)
    for t in TIERS:
        stats["by_model"][t] = 0
    return jsonify(stats)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
