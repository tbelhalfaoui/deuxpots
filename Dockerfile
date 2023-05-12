FROM python:3.11-slim

WORKDIR /app
COPY backend backend
COPY frontend/build frontend/build
RUN pip install -r backend/requirements.txt
CMD ["gunicorn", "--chdir", "backend", "deuxpots.app:app", "--bind", "0.0.0.0:8080"]
