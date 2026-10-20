import json
import sys

new = json.load(open("models/metrics.json"))
base = json.load(open("baselines.json"))

failed = False
for name in base:
    drop = base[name]["accuracy"] - new[name]["accuracy"]
    status = "FAIL" if drop > 0.02 else "OK"
    print(f"{name}: baseline={base[name]['accuracy']} "
          f"new={new[name]['accuracy']} drop={drop:.4f} {status}")
    if drop > 0.02:
        failed = True

sys.exit(1 if failed else 0)
