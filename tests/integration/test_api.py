import uuid
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.infrastructure.database.models import Outbox, Payment

pytestmark = pytest.mark.asyncio


async def test_create_payment_success(async_client: AsyncClient, db_session: AsyncSession) -> None:
    idempotency_key = str(uuid.uuid4())
    payload = {
        "amount": "150.50",
        "currency": "RUB",
        "description": "Integration test payment",
        "webhook_url": "https://example.com/webhook",
        "metadata": {"test_id": 123},
    }
    headers = {
        "X-API-Key": settings.app_api_key.get_secret_value(),
        "Idempotency-Key": idempotency_key,
    }

    response = await async_client.post("/api/v1/payments/", json=payload, headers=headers)

    assert response.status_code == 202
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"
    assert data["amount"] == "150.50"

    payment_id = data["id"]

    stmt = select(Payment).where(Payment.id == payment_id)
    db_payment = (await db_session.execute(stmt)).scalar_one_or_none()
    assert db_payment is not None
    assert db_payment.amount == Decimal("150.50")

    stmt_outbox = select(Outbox).where(Outbox.routing_key == "payments.new")
    outbox_msgs = (await db_session.execute(stmt_outbox)).scalars().all()

    assert len(outbox_msgs) == 1
    outbox_payload = outbox_msgs[0].payload
    assert outbox_payload["id"] == payment_id


async def test_create_payment_idempotency(async_client: AsyncClient) -> None:
    idempotency_key = "idem-key-999"
    payload = {
        "amount": "500.00",
        "currency": "USD",
        "description": "Idempotency test",
        "webhook_url": "https://example.com/webhook",
    }
    headers = {
        "X-API-Key": settings.app_api_key.get_secret_value(),
        "Idempotency-Key": idempotency_key,
    }

    response_1 = await async_client.post("/api/v1/payments/", json=payload, headers=headers)
    assert response_1.status_code == 202

    response_2 = await async_client.post("/api/v1/payments/", json=payload, headers=headers)

    assert response_2.status_code == 409
    assert "already exists" in response_2.json()["detail"]


async def test_get_payment_not_found(async_client: AsyncClient) -> None:
    random_uuid = str(uuid.uuid4())
    headers = {"X-API-Key": settings.app_api_key.get_secret_value()}

    response = await async_client.get(f"/api/v1/payments/{random_uuid}/", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"


async def test_auth_failure(async_client: AsyncClient) -> None:
    payload = {
        "amount": "100",
        "currency": "EUR",
        "description": "X",
        "webhook_url": "https://x.com",
    }
    headers = {"Idempotency-Key": "123"}

    response = await async_client.post("/api/v1/payments/", json=payload, headers=headers)

    assert response.status_code == 401
