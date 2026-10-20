FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY model_service/service.py .
COPY models/ models/
CMD ["python", "service.py"]
