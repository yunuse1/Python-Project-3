# Python backend Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY scripts/ ./scripts/
COPY analysis/ ./analysis/

EXPOSE 5000
CMD ["python", "src/app.py"]

