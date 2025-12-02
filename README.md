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
```

### Запуск приложения

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Приложение будет доступно по адресу: http://localhost:8000

Документация API: http://localhost:8000/docs

## Структура проекта

```
mosstroinform_backend/
├── app/
│   ├── api/              # API эндпоинты
│   ├── core/             # Конфигурация и базовые настройки
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic схемы
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
