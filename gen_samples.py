import json

from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

X, y = load_digits(return_X_y=True)
_, Xte, _, yte = train_test_split(X, y, test_size=0.3, random_state=42)
out = [{"x": x.astype(int).tolist(), "y": int(t)} for x, t in zip(Xte[:40], yte[:40])]
json.dump(out, open("router/samples.json", "w"))
print(len(out), "samples written")
