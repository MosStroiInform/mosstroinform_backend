# Техническое задание для разработки бэкенда API

## Общая информация

**Название проекта:** МосСтройИнформ Мобайл  
**Тип API:** REST API  
**Формат данных:** JSON  
**Кодировка:** UTF-8  
**Базовый URL:** Настраивается через конфигурацию (dev/staging/prod)

## Технические требования

### Общие требования

1. **Формат запросов/ответов:**
   - Content-Type: `application/json`
   - Accept: `application/json`
   - Все даты в формате ISO 8601: `YYYY-MM-DDTHH:mm:ss.sssZ` или `YYYY-MM-DDTHH:mm:ssZ`

2. **Таймауты:**
   - Connect timeout: 30 секунд
   - Receive timeout: 30 секунд

3. **Обработка ошибок:**
   - Стандартные HTTP коды статусов
   - Формат ошибки:
     ```json
     {
       "error": {
         "code": "ERROR_CODE",
         "message": "Описание ошибки"
       }
     }
     ```

4. **Аутентификация:**
   - В текущей версии мобильного приложения аутентификация не реализована
   - Рекомендуется подготовить API для будущей интеграции (например, JWT токены в заголовке `Authorization: Bearer <token>`)

---

## Эндпоинты API

### 1. Проекты (Projects)

#### 1.1. Получить список проектов

**Метод:** `GET`  
**Путь:** `/projects`  
**Описание:** Возвращает список всех доступных проектов строительства

**Параметры запроса:** Нет

**Ответ:** `200 OK`
```json
[
  {
    "id": "string",
    "name": "string",
    "address": "string",
    "description": "string",
    "area": 0.0,
    "floors": 0,
    "price": 0,
    "imageUrl": "string | null",
    "stages": [
      {
        "id": "string",
        "name": "string",
        "status": "pending | in_progress | completed"
      }
    ]
  }
]
```

**Пример ответа:**
```json
[
  {
    "id": "proj-001",
    "name": "Дом на участке 6 соток",
    "address": "Московская область, д. Примерное",
    "description": "Двухэтажный дом с гаражом",
    "area": 120.5,
    "floors": 2,
    "price": 5000000,
    "imageUrl": "https://example.com/images/proj-001.jpg",
    "stages": [
      {
        "id": "stage-001",
        "name": "Фундамент",
        "status": "completed"
      },
      {
        "id": "stage-002",
        "name": "Стены",
        "status": "in_progress"
      },
      {
        "id": "stage-003",
        "name": "Кровля",
        "status": "pending"
      }
    ]
  }
]
```

**Ошибки:**
- `500 Internal Server Error` - внутренняя ошибка сервера

---

#### 1.2. Получить проект по ID

**Метод:** `GET`  
**Путь:** `/projects/{id}`  
**Описание:** Возвращает детальную информацию о проекте

**Параметры пути:**
- `id` (string, required) - идентификатор проекта

**Ответ:** `200 OK`
```json
{
  "id": "string",
  "name": "string",
  "address": "string",
  "description": "string",
  "area": 0.0,
  "floors": 0,
  "price": 0,
  "imageUrl": "string | null",
  "stages": [
    {
      "id": "string",
      "name": "string",
      "status": "pending | in_progress | completed"
    }
  ]
}
```

**Ошибки:**
- `404 Not Found` - проект не найден
- `500 Internal Server Error` - внутренняя ошибка сервера

---

#### 1.3. Отправить запрос на строительство

**Метод:** `POST`  
**Путь:** `/projects/{id}/request`  
**Описание:** Отправляет запрос на начало строительства проекта

**Параметры пути:**
- `id` (string, required) - идентификатор проекта

**Тело запроса:** Нет (пустое тело)

**Ответ:** `200 OK` или `204 No Content`
```json
{}
```

**Ошибки:**
- `404 Not Found` - проект не найден
- `400 Bad Request` - некорректный запрос (например, проект уже в процессе строительства)
- `500 Internal Server Error` - внутренняя ошибка сервера

---

### 2. Документы (Documents)

#### 2.1. Получить список документов

**Метод:** `GET`  
**Путь:** `/documents`  
**Описание:** Возвращает список всех документов, требующих согласования

**Параметры запроса:** Нет

**Ответ:** `200 OK`
```json
[
  {
    "id": "string",
    "projectId": "string",
    "title": "string",
    "description": "string",
    "fileUrl": "string | null",
    "status": "pending | under_review | approved | rejected",
    "submittedAt": "2024-01-01T12:00:00Z | null",
    "approvedAt": "2024-01-01T12:00:00Z | null",
    "rejectionReason": "string | null"
  }
]
```

**Пример ответа:**
```json
[
  {
    "id": "doc-001",
    "projectId": "proj-001",
    "title": "Проектная документация",
    "description": "Полный комплект проектной документации",
    "fileUrl": "https://example.com/files/doc-001.pdf",
    "status": "under_review",
    "submittedAt": "2024-01-15T10:30:00Z",
    "approvedAt": null,
    "rejectionReason": null
  },
  {
    "id": "doc-002",
    "projectId": "proj-001",
    "title": "Разрешение на строительство",
    "description": "Официальное разрешение от местных властей",
    "fileUrl": "https://example.com/files/doc-002.pdf",
    "status": "approved",
    "submittedAt": "2024-01-10T09:00:00Z",
    "approvedAt": "2024-01-12T14:20:00Z",
    "rejectionReason": null
  }
]
```

**Ошибки:**
- `500 Internal Server Error` - внутренняя ошибка сервера

---

#### 2.2. Получить документ по ID

**Метод:** `GET`  
**Путь:** `/documents/{id}`  
**Описание:** Возвращает детальную информацию о документе

**Параметры пути:**
- `id` (string, required) - идентификатор документа

**Ответ:** `200 OK`
```json
{
  "id": "string",
  "projectId": "string",
  "title": "string",
  "description": "string",
  "fileUrl": "string | null",
  "status": "pending | under_review | approved | rejected",
  "submittedAt": "2024-01-01T12:00:00Z | null",
  "approvedAt": "2024-01-01T12:00:00Z | null",
  "rejectionReason": "string | null"
}
```

**Ошибки:**
- `404 Not Found` - документ не найден
- `500 Internal Server Error` - внутренняя ошибка сервера

---

#### 2.3. Одобрить документ

**Метод:** `POST`  
**Путь:** `/documents/{id}/approve`  
**Описание:** Одобряет документ

**Параметры пути:**
- `id` (string, required) - идентификатор документа

**Тело запроса:** Нет (пустое тело)

**Ответ:** `200 OK` или `204 No Content`
```json
{}
```

**Ошибки:**
- `404 Not Found` - документ не найден
- `400 Bad Request` - документ уже одобрен или отклонен
- `500 Internal Server Error` - внутренняя ошибка сервера

---

#### 2.4. Отклонить документ

**Метод:** `POST`  
**Путь:** `/documents/{id}/reject`  
**Описание:** Отклоняет документ с указанием причины

**Параметры пути:**
- `id` (string, required) - идентификатор документа

**Тело запроса:**
```json
{
  "reason": "string"
}
```

**Пример запроса:**
```json
{
  "reason": "Несоответствие требованиям по площади застройки"
}
```

**Ответ:** `200 OK` или `204 No Content`
```json
{}
```

**Ошибки:**
- `404 Not Found` - документ не найден
- `400 Bad Request` - документ уже одобрен или отклонен, отсутствует причина отклонения
- `500 Internal Server Error` - внутренняя ошибка сервера

---

### 3. Строительная площадка (Construction Site)

#### 3.1. Получить информацию о строительной площадке по проекту

**Метод:** `GET`  
**Путь:** `/construction-sites/project/{projectId}`  
**Описание:** Возвращает информацию о строительной площадке для указанного проекта

**Параметры пути:**
- `projectId` (string, required) - идентификатор проекта

**Ответ:** `200 OK`
```json
{
  "id": "string",
  "projectId": "string",
  "projectName": "string",
  "address": "string",
  "cameras": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "streamUrl": "string",
      "isActive": true,
      "thumbnailUrl": "string | null"
    }
  ],
  "startDate": "2024-01-01T12:00:00Z | null",
  "expectedCompletionDate": "2024-12-31T18:00:00Z | null",
  "progress": 0.0
}
```

**Пример ответа:**
```json
{
  "id": "site-001",
  "projectId": "proj-001",
  "projectName": "Дом на участке 6 соток",
  "address": "Московская область, д. Примерное",
  "cameras": [
    {
      "id": "cam-001",
      "name": "Камера 1 - Главный фасад",
      "description": "Обзор главного фасада здания",
      "streamUrl": "rtsp://example.com/stream/cam-001",
      "isActive": true,
      "thumbnailUrl": "https://example.com/thumbnails/cam-001.jpg"
    },
    {
      "id": "cam-002",
      "name": "Камера 2 - Задний двор",
      "description": "Обзор заднего двора и стройматериалов",
      "streamUrl": "rtsp://example.com/stream/cam-002",
      "isActive": true,
      "thumbnailUrl": "https://example.com/thumbnails/cam-002.jpg"
    }
  ],
  "startDate": "2024-01-15T08:00:00Z",
  "expectedCompletionDate": "2024-12-31T18:00:00Z",
  "progress": 0.355
}
```

**Ошибки:**
- `404 Not Found` - строительная площадка не найдена для указанного проекта
- `500 Internal Server Error` - внутренняя ошибка сервера

---

#### 3.2. Получить список камер строительной площадки

**Метод:** `GET`  
**Путь:** `/construction-sites/{siteId}/cameras`  
**Описание:** Возвращает список всех камер для строительной площадки

**Параметры пути:**
- `siteId` (string, required) - идентификатор строительной площадки

**Ответ:** `200 OK`
```json
[
  {
    "id": "string",
    "name": "string",
    "description": "string",
    "streamUrl": "string",
    "isActive": true,
    "thumbnailUrl": "string | null"
  }
]
```

**Ошибки:**
- `404 Not Found` - строительная площадка не найдена
- `500 Internal Server Error` - внутренняя ошибка сервера

---

#### 3.3. Получить информацию о камере

**Метод:** `GET`  
**Путь:** `/construction-sites/{siteId}/cameras/{cameraId}`  
**Описание:** Возвращает детальную информацию о конкретной камере

**Параметры пути:**
- `siteId` (string, required) - идентификатор строительной площадки
- `cameraId` (string, required) - идентификатор камеры

**Ответ:** `200 OK`
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "streamUrl": "string",
  "isActive": true,
  "thumbnailUrl": "string | null"
}
```

**Ошибки:**
- `404 Not Found` - камера или строительная площадка не найдены
- `500 Internal Server Error` - внутренняя ошибка сервера

---

### 4. Чат (Chat)

#### 4.1. Получить список чатов

**Метод:** `GET`  
**Путь:** `/chats`  
**Описание:** Возвращает список всех чатов пользователя

**Параметры запроса:** Нет

**Ответ:** `200 OK`
```json
[
  {
    "id": "string",
    "projectId": "string",
    "specialistName": "string",
    "specialistAvatarUrl": "string | null",
    "lastMessage": "string | null",
    "lastMessageAt": "2024-01-01T12:00:00Z | null",
    "unreadCount": 0,
    "isActive": true
  }
]
```

**Пример ответа:**
```json
[
  {
    "id": "chat-001",
    "projectId": "proj-001",
    "specialistName": "Иван Петров",
    "specialistAvatarUrl": "https://example.com/avatars/ivan.jpg",
    "lastMessage": "Добрый день! Как дела с документами?",
    "lastMessageAt": "2024-01-20T14:30:00Z",
    "unreadCount": 2,
    "isActive": true
  },
  {
    "id": "chat-002",
    "projectId": "proj-002",
    "specialistName": "Мария Сидорова",
    "specialistAvatarUrl": null,
    "lastMessage": "Спасибо за обращение!",
    "lastMessageAt": "2024-01-19T10:15:00Z",
    "unreadCount": 0,
    "isActive": true
  }
]
```

**Ошибки:**
- `500 Internal Server Error` - внутренняя ошибка сервера

---

#### 4.2. Получить информацию о чате

**Метод:** `GET`  
**Путь:** `/chats/{chatId}`  
**Описание:** Возвращает детальную информацию о чате

**Параметры пути:**
- `chatId` (string, required) - идентификатор чата

**Ответ:** `200 OK`
```json
{
  "id": "string",
  "projectId": "string",
  "specialistName": "string",
  "specialistAvatarUrl": "string | null",
  "lastMessage": "string | null",
  "lastMessageAt": "2024-01-01T12:00:00Z | null",
  "unreadCount": 0,
  "isActive": true
}
```

**Ошибки:**
- `404 Not Found` - чат не найден
- `500 Internal Server Error` - внутренняя ошибка сервера

---

#### 4.3. Получить сообщения чата

**Метод:** `GET`  
**Путь:** `/chats/{chatId}/messages`  
**Описание:** Возвращает список сообщений в чате

**Параметры пути:**
- `chatId` (string, required) - идентификатор чата

**Ответ:** `200 OK`
```json
[
  {
    "id": "string",
    "chatId": "string",
    "text": "string",
    "sentAt": "2024-01-01T12:00:00Z",
    "isFromSpecialist": false,
    "isRead": false
  }
]
```

**Пример ответа:**
```json
[
  {
    "id": "msg-001",
    "chatId": "chat-001",
    "text": "Добрый день! У меня вопрос по документам.",
    "sentAt": "2024-01-20T10:00:00Z",
    "isFromSpecialist": false,
    "isRead": true
  },
  {
    "id": "msg-002",
    "chatId": "chat-001",
    "text": "Здравствуйте! Конечно, задавайте вопросы.",
    "sentAt": "2024-01-20T10:05:00Z",
    "isFromSpecialist": true,
    "isRead": true
  },
  {
    "id": "msg-003",
    "chatId": "chat-001",
    "text": "Когда будет готов проект?",
    "sentAt": "2024-01-20T14:30:00Z",
    "isFromSpecialist": false,
    "isRead": false
  }
]
```

**Ошибки:**
- `404 Not Found` - чат не найден
- `500 Internal Server Error` - внутренняя ошибка сервера

---

#### 4.4. Отправить сообщение

**Метод:** `POST`  
**Путь:** `/chats/{chatId}/messages`  
**Описание:** Отправляет новое сообщение в чат

**Параметры пути:**
- `chatId` (string, required) - идентификатор чата

**Тело запроса:**
```json
{
  "text": "string"
}
```

**Пример запроса:**
```json
{
  "text": "Спасибо за информацию!"
}
```

**Ответ:** `200 OK` или `201 Created`
```json
{
  "id": "string",
  "chatId": "string",
  "text": "string",
  "sentAt": "2024-01-01T12:00:00Z",
  "isFromSpecialist": false,
  "isRead": false
}
```

**Ошибки:**
- `404 Not Found` - чат не найден
- `400 Bad Request` - пустое сообщение или некорректные данные
- `500 Internal Server Error` - внутренняя ошибка сервера

---

#### 4.5. Отметить сообщения как прочитанные

**Метод:** `POST`  
**Путь:** `/chats/{chatId}/messages/read`  
**Описание:** Отмечает все непрочитанные сообщения в чате как прочитанные

**Параметры пути:**
- `chatId` (string, required) - идентификатор чата

**Тело запроса:** Нет (пустое тело)

**Ответ:** `200 OK` или `204 No Content`
```json
{}
```

**Ошибки:**
- `404 Not Found` - чат не найден
- `500 Internal Server Error` - внутренняя ошибка сервера

---

### 5. Завершение строительства (Construction Completion)

#### 5.1. Получить статус завершения строительства

**Метод:** `GET`  
**Путь:** `/projects/{projectId}/completion-status`  
**Описание:** Возвращает статус завершения строительства проекта

**Параметры пути:**
- `projectId` (string, required) - идентификатор проекта

**Ответ:** `200 OK`
```json
{
  "projectId": "string",
  "isCompleted": false,
  "completionDate": "2024-12-31T18:00:00Z | null",
  "progress": 0.0,
  "documents": [
    {
      "id": "string",
      "title": "string",
      "description": "string",
      "fileUrl": "string | null",
      "status": "pending | signed | rejected",
      "submittedAt": "2024-01-01T12:00:00Z | null",
      "signedAt": "2024-01-01T12:00:00Z | null",
      "signatureUrl": "string | null"
    }
  ]
}
```

**Пример ответа:**
```json
{
  "projectId": "proj-001",
  "isCompleted": false,
  "completionDate": null,
  "progress": 0.85,
  "documents": [
    {
      "id": "final-doc-001",
      "title": "Акт приёмки-передачи",
      "description": "Документ о приёмке готового объекта",
      "fileUrl": "https://example.com/files/akt.pdf",
      "status": "pending",
      "submittedAt": "2024-12-15T10:00:00Z",
      "signedAt": null,
      "signatureUrl": null
    },
    {
      "id": "final-doc-002",
      "title": "Гарантийное обязательство",
      "description": "Гарантия на выполненные работы",
      "fileUrl": "https://example.com/files/garantia.pdf",
      "status": "signed",
      "submittedAt": "2024-12-10T09:00:00Z",
      "signedAt": "2024-12-12T14:30:00Z",
      "signatureUrl": "https://example.com/signatures/sig-002.png"
    }
  ]
}
```

**Ошибки:**
- `404 Not Found` - проект не найден
- `500 Internal Server Error` - внутренняя ошибка сервера

---

#### 5.2. Получить список финальных документов

**Метод:** `GET`  
**Путь:** `/projects/{projectId}/final-documents`  
**Описание:** Возвращает список всех финальных документов проекта

**Параметры пути:**
- `projectId` (string, required) - идентификатор проекта

**Ответ:** `200 OK`
```json
[
  {
    "id": "string",
    "title": "string",
    "description": "string",
    "fileUrl": "string | null",
    "status": "pending | signed | rejected",
    "submittedAt": "2024-01-01T12:00:00Z | null",
    "signedAt": "2024-01-01T12:00:00Z | null",
    "signatureUrl": "string | null"
  }
]
```

**Ошибки:**
- `404 Not Found` - проект не найден
- `500 Internal Server Error` - внутренняя ошибка сервера

---

#### 5.3. Получить финальный документ по ID

**Метод:** `GET`  
**Путь:** `/projects/{projectId}/final-documents/{documentId}`  
**Описание:** Возвращает детальную информацию о финальном документе

**Параметры пути:**
- `projectId` (string, required) - идентификатор проекта
- `documentId` (string, required) - идентификатор документа

**Ответ:** `200 OK`
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "fileUrl": "string | null",
  "status": "pending | signed | rejected",
  "submittedAt": "2024-01-01T12:00:00Z | null",
  "signedAt": "2024-01-01T12:00:00Z | null",
  "signatureUrl": "string | null"
}
```

**Ошибки:**
- `404 Not Found` - документ или проект не найдены
- `500 Internal Server Error` - внутренняя ошибка сервера

---

#### 5.4. Подписать финальный документ

**Метод:** `POST`  
**Путь:** `/projects/{projectId}/final-documents/{documentId}/sign`  
**Описание:** Подписывает финальный документ

**Параметры пути:**
- `projectId` (string, required) - идентификатор проекта
- `documentId` (string, required) - идентификатор документа

**Тело запроса:** Нет (пустое тело)

**Ответ:** `200 OK` или `204 No Content`
```json
{}
```

**Ошибки:**
- `404 Not Found` - документ или проект не найдены
- `400 Bad Request` - документ уже подписан или отклонен
- `500 Internal Server Error` - внутренняя ошибка сервера

---

#### 5.5. Отклонить финальный документ

**Метод:** `POST`  
**Путь:** `/projects/{projectId}/final-documents/{documentId}/reject`  
**Описание:** Отклоняет финальный документ с указанием причины

**Параметры пути:**
- `projectId` (string, required) - идентификатор проекта
- `documentId` (string, required) - идентификатор документа

**Параметры запроса (form-data или query):**
- `reason` (string, required) - причина отклонения

**Тело запроса (если используется JSON):**
```json
{
  "reason": "string"
}
```

**Ответ:** `200 OK` или `204 No Content`
```json
{}
```

**Ошибки:**
- `404 Not Found` - документ или проект не найдены
- `400 Bad Request` - документ уже подписан или отклонен, отсутствует причина отклонения
- `500 Internal Server Error` - внутренняя ошибка сервера

---

## Типы данных

### Статусы этапов строительства (Stage Status)
- `pending` - ожидает начала
- `in_progress` - в процессе выполнения
- `completed` - завершён

### Статусы документов (Document Status)
- `pending` - ожидает рассмотрения
- `under_review` - на рассмотрении
- `approved` - одобрен
- `rejected` - отклонён

### Статусы финальных документов (Final Document Status)
- `pending` - ожидает подписания
- `signed` - подписан
- `rejected` - отклонён

### Поле Progress (Прогресс выполнения)

Поле `progress` используется в следующих эндпоинтах:
- `/construction-sites/project/{projectId}` - прогресс строительства площадки
- `/projects/{projectId}/completion-status` - прогресс завершения проекта

**Формат:** `double` (число с плавающей точкой)  
**Диапазон:** от `0.0` до `1.0`  
**Описание:** Представляет долю выполнения от 0% до 100%
- `0.0` = 0% (не начато)
- `0.5` = 50% (половина выполнена)
- `1.0` = 100% (полностью выполнено)

**Примеры:**
- `0.0` - работа не начата
- `0.355` - выполнено 35.5%
- `0.85` - выполнено 85%
- `1.0` - работа полностью завершена

**Примечание:** В мобильном приложении это значение умножается на 100 для отображения в процентах пользователю.

---

## Рекомендации по реализации

### Технологический стек

1. **Фреймворк:** FastAPI (рекомендуется) или Flask/Django REST Framework
2. **База данных:** PostgreSQL (рекомендуется) или другая реляционная БД
3. **ORM:** SQLAlchemy (для FastAPI/Flask) или Django ORM
4. **Валидация:** Pydantic (для FastAPI) или Marshmallow (для Flask)
5. **Аутентификация:** JWT (для будущей интеграции)

### Структура проекта

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── projects.py
│   │   │   │   ├── documents.py
│   │   │   │   ├── construction_sites.py
│   │   │   │   ├── chats.py
│   │   │   │   └── completion.py
│   │   │   └── router.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── models/
│   │   ├── project.py
│   │   ├── document.py
│   │   ├── construction_site.py
│   │   ├── chat.py
│   │   └── completion.py
│   ├── schemas/
│   │   └── ...
│   └── services/
│       └── ...
├── tests/
├── requirements.txt
└── README.md
```

### Важные замечания

1. **Идентификаторы:** Используйте UUID для всех идентификаторов (рекомендуется) или строковые ID
2. **Даты:** Все даты должны быть в формате ISO 8601 с часовым поясом
3. **Файлы:** URL файлов должны быть абсолютными и доступными для скачивания
4. **Видеопотоки:** URL видеопотоков должны поддерживать протоколы RTSP или HLS для мобильного приложения
5. **Пагинация:** Для списков рекомендуется добавить пагинацию (в текущей версии не реализована, но стоит предусмотреть)
6. **Валидация:** Все входные данные должны валидироваться
7. **Ошибки:** Все ошибки должны возвращаться в едином формате

### Тестирование

Рекомендуется покрыть тестами:
- Все эндпоинты (unit тесты)
- Интеграционные тесты для критических сценариев
- Валидацию данных
- Обработку ошибок

---

## Примеры использования

### Пример запроса на получение проектов

```bash
curl -X GET "https://api.example.com/projects" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json"
```

### Пример запроса на отправку сообщения

```bash
curl -X POST "https://api.example.com/chats/chat-001/messages" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "text": "Добрый день! У меня вопрос."
  }'
```

### Пример запроса на отклонение документа

```bash
curl -X POST "https://api.example.com/documents/doc-001/reject" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "reason": "Несоответствие требованиям"
  }'
```

---

## Контакты и вопросы

При возникновении вопросов по спецификации обращайтесь к разработчикам мобильного приложения или к техническому руководителю проекта.

---

**Версия документа:** 1.0  
**Дата создания:** 2024-01-20  
**Последнее обновление:** 2024-01-20

