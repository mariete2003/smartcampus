FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Primero las dependencias (Docker las cachea si no cambian)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Usuario sin privilegios y carpeta para la base de datos
RUN useradd --create-home appuser \
    && mkdir -p /data \
    && chown appuser /data
USER appuser

ENV APP_ENV=production \
    APP_PORT=8000 \
    DB_PATH=/data/smartcampus.db

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen('http://localhost:' + os.getenv('APP_PORT', '8000') + '/health')"

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT}"]