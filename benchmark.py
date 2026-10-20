import statistics as st
import sys

import requests
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

URL = "http://localhost:9000/predict"
X, y = load_digits(return_X_y=True)
_, Xte, _, yte = train_test_split(X, y, test_size=0.3, random_state=42)
N = 200


def run(priority):
    ok, cost, lat, used = 0, 0, [], {}
    for x, t in zip(Xte[:N], yte[:N]):
        d = requests.post(URL, json={"features": x.tolist(),
                                     "priority": priority}).json()
        ok += d["label"] == t
        cost += d["cost"]
        lat.append(d["latency_ms"])
        used[d["model"]] = used.get(d["model"], 0) + 1
    return ok / N, cost / N, st.median(lat), used


h_acc, h_cost, h_lat, _ = run(True)
r_acc, r_cost, r_lat, used = run(False)
saving = 1 - r_cost / h_cost
retained = r_acc / h_acc

table = f"""| Strategy | Accuracy | Avg cost | Median latency (ms) |
|---|---|---|---|
| Always-heavy | {h_acc:.3f} | {h_cost:.2f} | {h_lat:.1f} |
| ModelMux | {r_acc:.3f} | {r_cost:.2f} | {r_lat:.1f} |

Cost saving: {saving:.1%} | Accuracy retained: {retained:.1%} | Usage: {used}
"""
print(table)
open("benchmark.md", "w").write(table)

if saving < 0.60 or retained < 0.95 or r_lat >= 100:
    sys.exit("benchmark criteria not met")
