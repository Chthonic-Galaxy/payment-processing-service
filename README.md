--- English &bull; [Русский](docs/README_ru.md) ---

# Async Payment Processing Service 🚀

Welcome! This is a production-ready, asynchronous microservice designed for high-load financial transactions. It processes payment requests, handles background execution via a message broker, and sends webhook notifications with guaranteed delivery.

The project is built with **Python 3.13**, **FastAPI**, **SQLAlchemy 2.0**, and **FastStream**, heavily emphasizing Clean/Hexagonal Architecture principles, SOLID, and enterprise integration patterns.

## Architectural Highlights

This isn't just a basic CRUD app. Here is what makes it tick under the hood:

- **Transactional Outbox Pattern:** Guarantees *at-least-once* message delivery. Payments and broker events are committed to PostgreSQL in a single ACID transaction. A dedicated background worker safely polls the database using `SELECT ... FOR UPDATE SKIP LOCKED` to prevent race conditions.
- **Idempotency:** Protects against double charges. If a client sends the same `Idempotency-Key` twice due to a network hiccup, the DB immediately rejects it, and the API safely returns a `409 Conflict`.
- **Fault Tolerance & Webhooks:** Bank emulation and webhook deliveries are handled via **RabbitMQ**. We use `tenacity` for exponential backoff retries (up to 3 attempts).
- **Dead Letter Queue (DLQ):** If a webhook server is permanently down and all retries fail, the message isn't lost. It's automatically routed to a `payments.dlq` queue for manual inspection.
- **Flawless Testing:** Zero mocks for infrastructure! Tests use **Testcontainers** to spin up real isolated instances of PostgreSQL and RabbitMQ.

## Tech Stack

- **Framework:** FastAPI, Pydantic v2
- **Broker:** RabbitMQ, FastStream
- **Database:** PostgreSQL, SQLAlchemy 2.0 (asyncpg), Alembic
- **Package Manager:** `uv`
- **Testing:** Pytest, pytest-asyncio, Testcontainers

## 🚀 Quick Start

### 1. Prepare Secrets
The project uses Docker secrets for security. Before starting, create a `secrets/` directory in the root folder and add the required passwords:

```bash
mkdir -p secrets
echo "your_secure_db_password" > secrets/pg_password.txt
echo "your_secure_rmq_password" > secrets/rabbitmq_password.txt
```

### 2. Run the Infrastructure
Spin up the entire ecosystem (Postgres, RabbitMQ, API, Consumer, and Outbox Worker) using Docker Compose:

```bash
docker compose up --build -d
```

Alembic migrations will run automatically upon startup.

### 3. Test the API
The API requires an authorization header (`X-API-Key`). By default, it's set to `secret-key`. You can view the interactive Swagger UI at[http://localhost:8000/docs](http://localhost:8000/docs).

**Create a Payment (cURL):**
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
  "description": "Test order",
  "webhook_url": "https://webhook.site/your-unique-url"
}'
```
*Tip: Use [webhook.site](https://webhook.site/) to generate a temporary URL and watch the asynchronous webhook arrive 2-5 seconds later!*

## 🧪 Running Tests

Integration tests use **Testcontainers**. Make sure you have a Docker daemon running on your host machine.

```bash
# Install dependencies using uv
uv sync

# Run the test suite
uv run pytest -v -s
```
Testcontainers will automatically pull the necessary Postgres and RabbitMQ images, run the tests in an isolated environment, and clean up afterward.

## 📂 Project Structure

```text
src/
├── api/             # FastAPI routers, dependencies, and Pydantic schemas
├── core/            # Domain entities, use cases, and interfaces (Clean Core)
├── infrastructure/  # SQLAlchemy models, FastStream adapters, Outbox worker, etc.
└── config.py        # Environment variables and app settings
tests/               # Integration tests with Testcontainers
```
