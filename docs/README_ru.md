--- [English](../README.md) &bull; Русский ---

# Асинхронный сервис процессинга платежей 🚀

Привет! Это готовый к продакшену асинхронный микросервис для обработки высоконагруженных финансовых транзакций. Он принимает запросы на оплату, эмулирует обработку через брокер сообщений и гарантированно доставляет результаты клиентам через вебхуки.

Проект написан на **Python 3.13**, **FastAPI**, **SQLAlchemy 2.0** и **FastStream**. Архитектура строго следует принципам Clean Architecture (Гексагональная архитектура), SOLID и использует энтерпрайз-паттерны интеграции.

## Ключевые архитектурные решения

Это не просто базовое CRUD-приложение. Вот что работает под капотом:

- **Transactional Outbox Pattern:** Гарантирует доставку сообщений (*at-least-once*). Платеж и событие для брокера сохраняются в PostgreSQL в рамках одной ACID-транзакции. Фоновый воркер безопасно читает БД используя `SELECT ... FOR UPDATE SKIP LOCKED`, что полностью исключает состояние гонки (race conditions) при масштабировании воркеров.
- **Идемпотентность:** Защита от двойных списаний. Если клиент (из-за проблем с сетью) пришлет один и тот же `Idempotency-Key` дважды, база данных мгновенно отклонит дубликат, а API корректно вернет статус `409 Conflict`.
- **Отказоустойчивость и Вебхуки:** Эмуляция банка и отправка вебхуков реализованы через **RabbitMQ**. Для отправки HTTP-запросов используется `tenacity` с политикой экспоненциальной задержки (до 3 попыток).
- **Dead Letter Queue (DLQ):** Если сервер клиента "лежит" и все попытки доставить вебхук провалились, сообщение не теряется. RabbitMQ автоматически перенаправляет его в очередь `payments.dlq` для ручного разбора.
- **Честное тестирование:** Никаких моков базы или брокера! Интеграционные тесты используют **Testcontainers**, поднимая настоящие изолированные контейнеры PostgreSQL и RabbitMQ прямо во время прогона тестов.

## Стек технологий

- **Фреймворк:** FastAPI, Pydantic v2
- **Брокер сообщений:** RabbitMQ, FastStream
- **База данных:** PostgreSQL, SQLAlchemy 2.0 (asyncpg), Alembic
- **Пакетный менеджер:** `uv`
- **Тестирование:** Pytest, pytest-asyncio, Testcontainers

## 🚀 Быстрый старт

### 1. Подготовка секретов
Проект использует Docker Secrets для безопасности. Перед запуском создайте папку `secrets/` в корне проекта и добавьте пароли:

```bash
mkdir -p secrets
echo "your_secure_db_password" > secrets/pg_password.txt
echo "your_secure_rmq_password" > secrets/rabbitmq_password.txt
```

### 2. Запуск инфраструктуры
Поднимите всю систему (Postgres, RabbitMQ, API, Consumer и Outbox Worker) одной командой через Docker Compose:

```bash
docker compose up --build -d
```

Миграции Alembic накатываются автоматически при старте.

### 3. Проверка API
Все эндпоинты защищены ключом авторизации (`X-API-Key`). По умолчанию это `secret-key`. Интерактивная документация Swagger доступна по адресу [http://localhost:8000/docs](http://localhost:8000/docs).

**Создание платежа (cURL):**
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'X-API-Key: secret-key' \
  -H 'Idempotency-Key: my-unique-tx-001' \
  -H 'Content-Type: application/json' \
  -d '{
  "amount": "150.50",
  "currency": "RUB",
  "description": "Тестовый заказ",
  "webhook_url": "https://webhook.site/your-unique-url"
}'
```
*Совет: Используйте сервис [webhook.site](https://webhook.site/) для генерации временного URL. Вы увидите, как асинхронный вебхук с результатом "банка" прилетит туда через 2-5 секунд!*

## 🧪 Запуск тестов

Для интеграционных тестов используется **Testcontainers**. Убедитесь, что у вас запущен Docker daemon (Docker Desktop, OrbStack или Colima).

```bash
# Установка зависимостей через uv
uv sync

# Запуск тестов
uv run pytest -v -s
```
Testcontainers сам скачает нужные образы Postgres и RabbitMQ, проведет тесты в кристально чистом окружении и удалит за собой контейнеры.

## 📂 Структура проекта

```text
src/
├── api/             # FastAPI роутеры, зависимости (DI) и Pydantic схемы
├── core/            # Доменные сущности, Use Cases и интерфейсы (Чистое ядро)
├── infrastructure/  # Модели SQLAlchemy, адаптеры FastStream, Outbox-воркер и т.д.
└── config.py        # Настройки приложения (pydantic-settings)
tests/               # Интеграционные тесты
```
