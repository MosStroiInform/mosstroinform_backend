# syntax=docker/dockerfile:1
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Системные зависимости для psycopg/алембика
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

ENV APP_MODULE=app.main:app \
    HOST=0.0.0.0 \
    PORT=8000

# Устанавливаем права на выполнение для entrypoint.sh
# Делаем это после COPY, чтобы права сохранились даже при volume mount
RUN chmod +x docker/entrypoint.sh || true

EXPOSE 8000

# Используем sh для запуска, чтобы избежать проблем с правами
ENTRYPOINT ["sh", "docker/entrypoint.sh"]

