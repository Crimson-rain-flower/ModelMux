# ModelMux
Cost- and latency-aware multi-model inference router with Jenkins CI/CD.

Local run (Windows):
    pip install -r requirements-dev.txt
    python train.py
    docker compose up --build -d
    python smoke_test.py
    python benchmark.py

Jenkinsfile = Windows (bat). Jenkinsfile.linux = Linux/WSL (sh).
baselines.json = accuracy baselines for the quality gate.
Failed-run demo: Build with Parameters -> tick BREAK_MODEL.

Dashboard (UI): after `docker compose up --build -d` open http://localhost:8000
