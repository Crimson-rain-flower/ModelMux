import sys
import time

import requests
from sklearn.datasets import load_digits

URL = "http://localhost:9000"
x = load_digits().data[0].tolist()

for _ in range(30):                      # wait for the router to come up
    try:
        if requests.get(f"{URL}/health", timeout=2).ok:
            break
    except Exception:
        time.sleep(2)
else:
    sys.exit("router not reachable")

degraded_mode = len(sys.argv) > 1 and sys.argv[1] == "degraded"
body = {"features": x, "priority": degraded_mode}
d = requests.post(f"{URL}/predict", json=body, timeout=5).json()
print(d)

assert "label" in d
if degraded_mode:
    assert d["degraded"] is True
