FROM python:3.11-slim

WORKDIR /app
COPY backend backend
COPY frontend/build frontend/build

WORKDIR /app/backend
RUN pip install -r requirements.txt
RUN mkdir -p prometheus-temp
ENV PROMETHEUS_MULTIPROC_DIR=prometheus-temp
CMD ["gunicorn", "deuxpots.app:app", "--bind", "0.0.0.0:8080"]
