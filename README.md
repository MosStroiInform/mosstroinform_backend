# MosStroiInform Backend API

REST API для мобильного приложения МосСтройИнформ.

## Технологический стек

- **FastAPI** - веб-фреймворк
- **PostgreSQL** - база данных
- **SQLAlchemy** - ORM
- **Alembic** - миграции базы данных
- **Pydantic** - валидация данных

## Установка и запуск

### Требования

- Python 3.10+
- PostgreSQL 12+

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Настройка окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` и укажите параметры подключения к базе данных.

### Инициализация базы данных

```bash
# Создание миграций
alembic revision --autogenerate -m "Initial migration"

# Применение миграций
alembic upgrade head

# Заполнение тестовыми данными (опционально)
python -m app.scripts.seed_data
```

### Запуск приложения

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Приложение будет доступно по адресу: http://localhost:8000

Документация API: http://localhost:8000/docs

## Запуск в Docker / Docker Compose

### Основные переменные (могут переопределяться в .env или через окружение)
- `POSTGRES_DB` (default: `mosstroinform_db`)
- `POSTGRES_USER` (default: `app_user`)
- `POSTGRES_PASSWORD` (default: `app_password`)
- `POSTGRES_HOST` (default: `db`)
- `POSTGRES_PORT` (default: `5432`)
- `APP_PORT` (default: `8000`) — внешний порт сервиса
- `DATABASE_URL` (default формируется автоматически на базе параметров выше)
- `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`

### Шаги
```bash
# 1) Скопировать и настроить окружение (опционально, если нужны отличия от дефолта)
cp .env.example .env  # или создайте свой .env с нужными значениями

# 2) Собрать и поднять контейнеры
docker compose up -d --build

# 3) Применить миграции (выполняется автоматически в entrypoint), но можно запустить вручную:
docker compose exec backend alembic upgrade head

# 4) (Опционально) Засидить тестовые данные
docker compose exec backend python -m app.scripts.seed_data

# 5) Проверить, что API поднято
curl http://localhost:8000/
```

### Остановка и очистка
```bash
docker compose down           # остановить
docker compose down -v        # остановить и удалить volume с данными БД
```

## Структура проекта

```
mosstroinform_backend/
├── app/
│   ├── api/              # API эндпоинты
│   ├── core/             # Конфигурация и базовые настройки
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic схемы
│   ├── scripts/          # Скрипты (seed data и др.)
│   └── main.py           # Точка входа приложения
├── alembic/              # Миграции базы данных
├── tests/                # Тесты
└── requirements.txt      # Зависимости
```

## API Endpoints

### Проекты
- `GET /api/v1/projects` - Список проектов
- `GET /api/v1/projects/{id}` - Детали проекта
- `POST /api/v1/projects/{id}/request` - Запрос на строительство

### Документы
- `GET /api/v1/documents` - Список документов
- `GET /api/v1/documents/{id}` - Детали документа
- `POST /api/v1/documents/{id}/approve` - Одобрить документ
- `POST /api/v1/documents/{id}/reject` - Отклонить документ

### Строительная площадка
- `GET /api/v1/construction-sites/project/{projectId}` - Информация о площадке
- `GET /api/v1/construction-sites/{siteId}/cameras` - Список камер
- `GET /api/v1/construction-sites/{siteId}/cameras/{cameraId}` - Детали камеры

### Чат
- `GET /api/v1/chats` - Список чатов
- `GET /api/v1/chats/{chatId}` - Детали чата
- `GET /api/v1/chats/{chatId}/messages` - Сообщения чата
- `POST /api/v1/chats/{chatId}/messages` - Отправить сообщение
- `POST /api/v1/chats/{chatId}/messages/read` - Отметить как прочитанные

### Завершение строительства
- `GET /api/v1/projects/{projectId}/completion-status` - Статус завершения
- `GET /api/v1/projects/{projectId}/final-documents` - Финальные документы
- `GET /api/v1/projects/{projectId}/final-documents/{documentId}` - Детали документа
- `POST /api/v1/projects/{projectId}/final-documents/{documentId}/sign` - Подписать документ
- `POST /api/v1/projects/{projectId}/final-documents/{documentId}/reject` - Отклонить документ

## Разработка

Проект использует ветвление по этапам:
- `stage` - основная ветка разработки
- `stage-XX-*` - ветки для каждого этапа разработки

После завершения каждого этапа ветка мержится в `stage` через squash merge.

## Тестирование

Для запуска тестов:

```bash
# Установка зависимостей для тестирования
pip install -r requirements.txt

# Запуск всех тестов
pytest

# Запуск с подробным выводом
pytest -v

# Запуск конкретного теста
pytest tests/test_projects.py
```

Тесты используют SQLite в памяти, поэтому не требуют настройки PostgreSQL для тестирования.

## Лицензия

MIT
