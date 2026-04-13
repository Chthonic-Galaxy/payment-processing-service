import asyncio
import logging
import random
from typing import Any

from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue

from src.config import settings
from src.core.entities.payment import PaymentStatus
from src.infrastructure.database.connection import async_session_factory
from src.infrastructure.database.repositories.payments import SQLAlchemyPaymentRepository
from src.infrastructure.webhook.client import WebhookClient

logger = logging.getLogger(__name__)

broker = RabbitBroker(settings.broker.url)
app = FastStream(broker)

dlq = RabbitQueue("payments.dlq")

main_queue = RabbitQueue(
    name="payments.new",
    routing_key="payments.new",
    arguments={
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": "payments.dlq",
    },
)

webhook_client = WebhookClient()


@broker.subscriber(queue=main_queue)
async def process_payment(message: dict[str, Any]) -> None:
    payment_id = message.get("id")
    webhook_url = message.get("webhook_url")

    logger.info(f"Received payment {payment_id} for processing")

    processing_time = random.uniform(2, 5)
    await asyncio.sleep(processing_time)

    # Emulation of Bank Success/Failure (90% Success, 10% Failure)
    is_success = random.random() < 0.90
    new_status = PaymentStatus.SUCCEEDED if is_success else PaymentStatus.FAILED

    async with async_session_factory.begin() as session:
        repo = SQLAlchemyPaymentRepository(session)
        await repo.update_status(payment_id=payment_id, status=new_status)  # pyright: ignore[reportArgumentType]

    logger.info(f"Payment {payment_id} processed with status: {new_status.value}")

    webhook_payload = {
        "payment_id": payment_id,
        "status": new_status.value,
        "amount": message.get("amount"),
        "currency": message.get("currency"),
    }

    try:
        await webhook_client.send(url=webhook_url, payload=webhook_payload)  # pyright: ignore[reportArgumentType]
    except Exception as e:
        logger.error(f"Failed to deliver webhook for payment {payment_id}. Sending to DLQ.")
        raise e
