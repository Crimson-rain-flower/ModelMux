import json
import os
import time

import joblib
from sklearn.datasets import load_digits
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

X, y = load_digits(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=42)

# BREAK=1 deliberately cripples the light model (for the failed-run demo)
n = 40 if os.getenv("BREAK") == "1" else len(Xtr)

models = {
    "light": (LogisticRegression(C=0.05, max_iter=2000), Xtr[:n], ytr[:n]),
    "mid": (RandomForestClassifier(n_estimators=100, random_state=0), Xtr, ytr),
    "heavy": (SVC(C=10, gamma=0.001, probability=True, random_state=0), Xtr, ytr),
}

os.makedirs("models", exist_ok=True)
metrics = {}
for name, (m, a, b) in models.items():
    m.fit(a, b)
    t0 = time.time()
    pred = m.predict(Xte)
    ms = (time.time() - t0) * 1000 / len(Xte)
    path = f"models/{name}.joblib"
    joblib.dump(m, path)
    metrics[name] = {
        "version": "1.0",
        "accuracy": round(accuracy_score(yte, pred), 4),
        "f1": round(f1_score(yte, pred, average="macro"), 4),
        "size_kb": round(os.path.getsize(path) / 1024),
        "latency_ms": round(ms, 3),
    }

with open("models/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)
print(json.dumps(metrics, indent=2))
