FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir flask==3.0.3 requests==2.32.3
COPY router/router.py router/index.html router/samples.json ./
CMD ["python", "router.py"]
