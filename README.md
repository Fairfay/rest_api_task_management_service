# REST API Сервис для управления заявками на выплату

REST API сервис для управления заявками на выплату средств с асинхронной обработкой через Celery и Redis.

## Возможности

- **RESTful API** для управления заявками на выплату (CRUD операции)
- **Асинхронная обработка** через Celery для фоновых задач
- **Валидация данных** заявок на выплату
- **Документация API** через Swagger/OpenAPI
- **Поддержка Docker** для удобного развертывания
- **Тесты** с использованием pytest
- **Минимальная типизация**

## Технологический стек

- **Python 3.10+**
- **Django 4.2+**
- **Django REST Framework**
- **Celery 5.3+** с Redis в качестве брокера сообщений
- **PostgreSQL** в качестве базы данных
- **Poetry** для управления зависимостями
- **Docker & Docker Compose** для контейнеризации
- **nplusone** для поиска дубликатов
- **drf-standardized-errors** для единого вида ошибок,
- **django-telegram-logging** для мгновенной отправки сообщений в телеграм при критической ошибке",
- **drf-spectacular** для документации,
- **django-health-check** для быстрой оценки работоспособности",
- **flower** для отслеживания celery тасок,
- **pytest** для тестирования,

## Быстрый старт

### Установка зависимостей

1. **Установите Poetry** (если еще не установлен):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Установите зависимости проекта**:
   ```bash
   poetry install
   ```

### Настройка окружения

1. **Создайте файл `.env`** на основе `.env.template`:
   ```bash
   cp .env.template .env
   ```

2. **Заполните переменные окружения** в файле `.env`:

### Запуск миграций

Миграции применяются автоматически!

### Запуск приложения

#### Запуск через Docker Compose (рекомендуется)

**Запустите все сервисы**:
   ```bash
   docker compose up -d --build
   ```
   
   Или через make:
   ```bash
   make docker-dev
   ```

### Требуется для доступа к документации.
**Создайте суперпользователя**:
   ```bash
   docker compose exec -it rest_api_task_management_service-web-1 bash
   ```
   ```bash
   python manage.py createsuperuser
   ```

**Остановка сервисов**:
   ```bash
   docker compose down
   ```
   
   Или через make:
   ```bash
   make docker-down
   ```

### Запуск тестов

Запустите тесты с помощью pytest:

```bash
poetry run pytest
```

Или через make:
```bash
make test
```

**Запуск тестов с подробным выводом**:
```bash
poetry run pytest -v
```

Или:
```bash
make test-verbose
```

**Запуск тестов с покрытием кода**:
```bash
poetry run pytest --cov=payouts --cov=server --cov-report=html --cov-report=term
```

Или:
```bash
make test-coverage
```

## API Endpoints

### Заявки на выплату

- `GET /api/v1/payouts/` - Список всех заявок (с пагинацией)
- `GET /api/v1/payouts/{id}/` - Получить заявку по ID
- `POST /api/v1/payouts/` - Создать новую заявку
- `PATCH /api/v1/payouts/{id}/` - Обновить заявку (частично)
- `DELETE /api/v1/payouts/{id}/` - Удалить заявку

### Документация API

После запуска приложения доступна документация:

- **Swagger UI**: `http://localhost:8000/api/v1/schema/swagger-ui/`
- **ReDoc**: `http://localhost:8000/api/v1/schema/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/v1/schema/`

### Пример запроса

```bash
# Создание заявки на выплату
curl -X POST http://localhost:8000/api/v1/payouts/ \
  -H "Content-Type: application/json" \
  -d '{
    "payment_sum": "1000.00",
    "currency": "USD",
    "recipients_details": "Bank Account: 1234567890, SWIFT: ABCDUS33",
    "comment": "Ежемесячная выплата зарплаты"
  }'
```

## Доступные команды Make

- `make run` - Запустить Django сервер разработки
- `make test` - Запустить тесты
- `make test-verbose` - Запустить тесты с подробным выводом
- `make test-coverage` - Запустить тесты с покрытием кода
- `make docker-dev` - Запустить development окружение в Docker
- `make docker-prod` - Запустить production окружение в Docker
- `make docker-down` - Остановить Docker контейнеры
- `make clean` - Очистить кэш Python файлов

## Обработка заявок через Celery

При создании заявки на выплату через API:

1. Заявка сохраняется со статусом `open`
2. Автоматически запускается Celery задача `process_payout` для асинхронной обработки
3. Задача:
   - Меняет статус на `in_progress`
   - Имитирует обработку
   - Выполняет проверки
   - Меняет статус на `resolved`
4. API возвращает ответ сразу, не дожидаясь обработки

## Деплой в продакшн

### Представление о деплое проекта в прод

Проект разворачивается в контейнеризированной среде с использованием Docker Compose, еще лучшедоложить conf для кубера.
Желательно держать БД и redis ужен запущенными на другом сервере, и донастроить prod-compose. Основной подход:

1. **Контейнеризация**: Все сервисы упакованы в Docker-контейнеры для изоляции и воспроизводимости
2. **Микросервисная архитектура**: Разделение на независимые сервисы (web, worker, database, broker)
3. **Обратный прокси**: Nginx для маршрутизации запросов, SSL-termination и статики(есть папка deploy)
4. **Мониторинг**: Логирование, метрики и health checks для отслеживания состояния системы

### Необходимые сервисы

Для полноценной работы в продакшене требуются следующие сервисы:

1. **Web Application** (Django + Gunicorn) - обработка HTTP-запросов и REST API
2. **Database** (PostgreSQL) - хранение данных заявок на выплату
3. **Message Broker** (Redis) - брокер сообщений для Celery, кэширование
4. **Task Worker** (Celery Worker) - асинхронная обработка заявок
5. **Task Scheduler** (Celery Beat, опционально) - периодические задачи
6. **Reverse Proxy** (Nginx) - маршрутизация, SSL/TLS, статика
7. **Monitoring** (опционально) - Flower для Celery, Prometheus/Grafana для метрик

## Структура проекта

```
rest_api_task_management_service/
├── payouts/              # Основное приложение для управления выплатами
│   ├── models.py        # Модель PayoutRequest
│   ├── serializers.py   # DRF сериализаторы с валидацией
│   ├── views.py         # API viewset
│   └── pytest_tests/    # Тесты
├── server/              # Настройки Django проекта
│   ├── settings.py      # Конфигурация Django
│   ├── settings_test.py # Настройки для тестов
│   ├── urls.py          # Основная конфигурация URL
│   ├── celery.py        # Настройка Celery
│   └── tasks.py         # Celery задачи
├── docker-compose.yml   # Docker setup для разработки
├── docker-compose.prod.yml  # Docker setup для продакшена
├── Dockerfile           # Определение Docker образа
├── Makefile             # Общие команды
├── pytest.ini           # Конфигурация pytest
└── README.md            # Этот файл
```


## Автор
Тычин Денис

