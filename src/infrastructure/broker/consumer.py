import asyncio
import logging
import random
from typing import Any

from faststream import FastStream

from src.config import settings
from src.core.entities.payment import PaymentStatus
from src.infrastructure.broker.rabbit import broker, main_queue
from src.infrastructure.database.connection import async_session_factory
from src.infrastructure.database.repositories.payments import SQLAlchemyPaymentRepository
from src.infrastructure.logger import setup_logging
from src.infrastructure.webhook.client import WebhookClient

setup_logging(settings.log_level)
logger = logging.getLogger(__name__)

app = FastStream(broker)

webhook_client = WebhookClient()


@broker.subscriber(queue=main_queue)
async def process_payment(message: dict[str, Any]) -> None:
    """Process a payment message from RabbitMQ.

    Args:
        message: Payment message payload from the broker.
    """

    payment_id = message.get("id")
    webhook_url = message.get("webhook_url")

    logger.info("Received payment %s for processing", payment_id)

    processing_time = random.uniform(2, 5)
    await asyncio.sleep(processing_time)

    is_success = random.random() < 0.90
    new_status = PaymentStatus.SUCCEEDED if is_success else PaymentStatus.FAILED

    async with async_session_factory.begin() as session:
        repo = SQLAlchemyPaymentRepository(session)
        await repo.update_status(payment_id=payment_id, status=new_status)  # pyright: ignore[reportArgumentType]

    logger.info("Payment %s processed with status %s", payment_id, new_status.value)

    webhook_payload = {
        "payment_id": payment_id,
        "status": new_status.value,
        "amount": message.get("amount"),
        "currency": message.get("currency"),
    }

    try:
        await webhook_client.send(url=webhook_url, payload=webhook_payload)  # pyright: ignore[reportArgumentType]
    except Exception:
        logger.exception(
            "Failed to deliver webhook for payment %s. Message will be sent to DLQ.",
            payment_id,
        )
        raise
