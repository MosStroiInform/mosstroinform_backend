# MosStroiInform Backend API

REST API для мобильного приложения МосСтройИнформ.

## Технологический стек

**Backend API:**
- **FastAPI** - веб-фреймворк
- **PostgreSQL** - база данных
- **SQLAlchemy** - ORM
- **Alembic** - миграции базы данных
- **Pydantic** - валидация данных

**WebSocket сервис:**
- **Spring Boot 4.0** - фреймворк
- **Spring WebFlux** - реактивный веб-слой
- **Spring Data R2DBC** - реактивный доступ к БД
- **WebSocket** - протокол для обмена сообщениями в реальном времени
- **Java 21** - язык программирования

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

**Backend API:**
- `POSTGRES_DB` (default: `mosstroinform_db`)
- `POSTGRES_USER` (default: `app_user`)
- `POSTGRES_PASSWORD` (default: `app_password`)
- `POSTGRES_HOST` (default: `db`)
- `POSTGRES_PORT` (default: `5432`)
- `APP_PORT` (default: `8000`) — внешний порт сервиса
- `DATABASE_URL` (default формируется автоматически на базе параметров выше)
- `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`

**WebSocket сервис:**
- `DB_URL` (default: `r2dbc:postgresql://db:5432/mosstroinform_db`) — URL подключения к БД для R2DBC
- `DB_USERNAME` (default: значение из `POSTGRES_USER`)
- `DB_PASSWORD` (default: значение из `POSTGRES_PASSWORD`)
- `WS_PORT` (default: `8080`) — порт WebSocket сервера

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

# 6) Проверить, что WebSocket сервис запущен
curl http://localhost:8080/actuator/health  # если доступен health endpoint
# или проверьте логи
docker compose logs websocket
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

## WebSocket API

WebSocket сервис предоставляет возможность обмена сообщениями в реальном времени для чатов.

### Подключение

WebSocket сервис доступен по адресу:
```
ws://localhost:{WS_PORT}/chat/{chatId}
```

Где:
- `{WS_PORT}` - порт WebSocket сервера (по умолчанию: `8080`)
- `{chatId}` - UUID чата

**Пример:**
```
ws://localhost:8080/chat/123e4567-e89b-12d3-a456-426614174000
```

### Формат сообщений

Все сообщения отправляются и получаются в формате JSON.

#### Отправка сообщения (CREATE)

Для создания нового сообщения отправьте:

```json
{
  "type": "CREATE",
  "text": "Текст сообщения",
  "fromSpecialist": true
}
```

**Поля:**
- `type` (обязательно) - тип действия, должен быть `"CREATE"`
- `text` (обязательно) - текст сообщения
- `fromSpecialist` (обязательно) - `true` если сообщение от специалиста, `false` если от клиента

#### Отметка сообщения как прочитанного (READ)

Для отметки сообщения как прочитанного отправьте:

```json
{
  "type": "READ",
  "messageId": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Поля:**
- `type` (обязательно) - тип действия, должен быть `"READ"`
- `messageId` (обязательно) - UUID сообщения, которое нужно отметить как прочитанное

### Получение сообщений

Сервер отправляет все сообщения чата в формате `ChatMessage`:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "chatId": "123e4567-e89b-12d3-a456-426614174000",
  "text": "Текст сообщения",
  "fromSpecialist": true,
  "read": false,
  "sentAt": "2024-01-15T10:30:00",
  "createAt": "2024-01-15T10:30:00"
}
```

**Поля:**
- `id` - UUID сообщения
- `chatId` - UUID чата
- `text` - текст сообщения
- `fromSpecialist` - `true` если от специалиста, `false` если от клиента
- `read` - статус прочтения (`true` - прочитано, `false` - не прочитано)
- `sentAt` - дата и время отправки (ISO 8601)
- `createAt` - дата и время создания (ISO 8601)

### Примеры использования

#### JavaScript (браузер)

```javascript
const chatId = '123e4567-e89b-12d3-a456-426614174000';
const ws = new WebSocket(`ws://localhost:8080/chat/${chatId}`);

// Обработка входящих сообщений
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Получено сообщение:', message);
};

// Отправка сообщения
function sendMessage(text, fromSpecialist) {
  const message = {
    type: 'CREATE',
    text: text,
    fromSpecialist: fromSpecialist
  };
  ws.send(JSON.stringify(message));
}

// Отметка сообщения как прочитанного
function markAsRead(messageId) {
  const message = {
    type: 'READ',
    messageId: messageId
  };
  ws.send(JSON.stringify(message));
}

// Подключение
ws.onopen = () => {
  console.log('WebSocket подключен');
  sendMessage('Привет!', false);
};

ws.onerror = (error) => {
  console.error('WebSocket ошибка:', error);
};

ws.onclose = () => {
  console.log('WebSocket отключен');
};
```

#### Python

```python
import asyncio
import json
import websockets
from uuid import UUID

async def chat_client(chat_id: str):
    uri = f"ws://localhost:8080/chat/{chat_id}"
    
    async with websockets.connect(uri) as websocket:
        # Отправка сообщения
        message = {
            "type": "CREATE",
            "text": "Привет из Python!",
            "fromSpecialist": False
        }
        await websocket.send(json.dumps(message))
        
        # Получение сообщений
        async for message in websocket:
            data = json.loads(message)
            print(f"Получено: {data}")

# Запуск
asyncio.run(chat_client("123e4567-e89b-12d3-a456-426614174000"))
```

### Запуск WebSocket сервиса

WebSocket сервис запускается автоматически при использовании Docker Compose:

```bash
docker compose up -d
```

Или только WebSocket сервис:

```bash
docker compose up -d websocket
```

### Переменные окружения WebSocket сервиса

- `DB_URL` - URL подключения к базе данных (R2DBC формат, по умолчанию: `r2dbc:postgresql://db:5432/mosstroinform_db`)
- `DB_USERNAME` - имя пользователя БД (по умолчанию: значение из `POSTGRES_USER`)
- `DB_PASSWORD` - пароль БД (по умолчанию: значение из `POSTGRES_PASSWORD`)
- `WS_PORT` - порт WebSocket сервера (по умолчанию: `8080`)

### Особенности

- **Автоматическая синхронизация**: Все участники чата получают новые сообщения и обновления статуса прочтения в реальном времени
- **Валидация**: Сообщения валидируются на сервере, невалидные сообщения игнорируются
- **Безопасность**: Сообщения можно отмечать как прочитанные только в рамках того же чата
- **Обработка ошибок**: При ошибках десериализации сообщение логируется и игнорируется, соединение не разрывается

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

## Вклад разработчиков

### vasmarfas
- Инициализация проекта и архитектура
- Модели базы данных (SQLAlchemy)
- Pydantic схемы (Request/Response)
- API эндпоинты: проекты, документы, чат, завершение строительства
- Синхронизация API с мобильным приложением

### mever01
- Эндпоинты строительной площадки
- Обработка ошибок и middleware
- Тестирование и документация
- Обновления зависимостей и конфигурация
- Docker Compose инфраструктура

## Лицензия

MIT
