#!/bin/sh
set -e

echo "Waiting for database..."
python - <<'PY'
import os
import sys
import time
from sqlalchemy.engine import make_url
from psycopg import connect
from app.core.config import settings

def build_url():
    # Берём DATABASE_URL из окружения, если есть; иначе собираем из POSTGRES_*
    raw_url = os.getenv("DATABASE_URL")
    if not raw_url:
        user = os.getenv("POSTGRES_USER", "app_user")
        pwd = os.getenv("POSTGRES_PASSWORD", "app_password")
        host = os.getenv("POSTGRES_HOST", "db")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "mosstroinform_db")
        raw_url = f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{db}"

    url = make_url(raw_url)

    # Если в URL указан localhost/127.0.0.1, а задан POSTGRES_HOST, заменяем на него
    if url.host in ("localhost", "127.0.0.1") and os.getenv("POSTGRES_HOST"):
        url = url.set(host=os.getenv("POSTGRES_HOST"))

    return url

url = build_url()

for attempt in range(30):
    try:
        conn = connect(
            host=url.host,
            port=url.port or 5432,
            user=url.username,
            password=url.password,
            dbname=url.database,
        )
        conn.close()
        sys.exit(0)
    except Exception as exc:
        print(f"DB not ready ({exc}); retry {attempt + 1}/30")
        time.sleep(1)

print("Database connection timed out")
sys.exit(1)
PY

echo "Applying migrations..."
alembic upgrade head

echo "Starting Uvicorn..."
exec uvicorn "${APP_MODULE:-app.main:app}" --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}"

