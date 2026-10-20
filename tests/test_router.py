import sys

sys.path.insert(0, "router")
import router as r  # noqa: E402


def fake(conf, down=()):
    def f(tier, feats):
        if tier in down:
            raise ConnectionError
        return {"label": 1, "confidence": conf[tier], "model": tier}
    return f


def post(body):
    return r.app.test_client().post("/predict", json=body)


def test_light_serves_easy(monkeypatch):
    monkeypatch.setattr(r, "call", fake({"light": .99, "mid": .99, "heavy": .99}))
    d = post({"features": [0]}).get_json()
    assert d["model"] == "light" and d["cost"] == 1


def test_escalates_to_heavy(monkeypatch):
    monkeypatch.setattr(r, "call", fake({"light": .5, "mid": .5, "heavy": .9}))
    d = post({"features": [0]}).get_json()
    assert d["model"] == "heavy" and d["cost"] == 15


def test_priority_goes_heavy(monkeypatch):
    monkeypatch.setattr(r, "call", fake({"light": .99, "mid": .99, "heavy": .99}))
    d = post({"features": [0], "priority": True}).get_json()
    assert d["model"] == "heavy" and d["cost"] == 10


def test_degrades_when_heavy_down(monkeypatch):
    monkeypatch.setattr(r, "call", fake({"light": .9, "mid": .9, "heavy": .9},
                                        down=("heavy",)))
    d = post({"features": [0], "priority": True}).get_json()
    assert d["model"] == "mid" and d["degraded"] is True


def test_all_down(monkeypatch):
    monkeypatch.setattr(r, "call", fake({}, down=("light", "mid", "heavy")))
    assert post({"features": [0]}).status_code == 503
