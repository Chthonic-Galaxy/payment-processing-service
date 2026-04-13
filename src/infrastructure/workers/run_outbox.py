import asyncio
import logging

from src.config import settings
from src.infrastructure.broker.faststream_broker import FastStreamRabbitBroker
from src.infrastructure.broker.rabbit import broker
from src.infrastructure.database.connection import async_session_factory
from src.infrastructure.logger import setup_logging
from src.infrastructure.workers.outbox_processor import OutboxProcessor

setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Run the outbox processor worker."""

    logger.info("Connecting outbox worker to RabbitMQ")
    await broker.connect()

    rabbit_adapter = FastStreamRabbitBroker(broker)

    processor = OutboxProcessor(session_factory=async_session_factory, broker=rabbit_adapter)

    try:
        logger.info("Starting outbox processor")
        await processor.start()
    finally:
        logger.info("Stopping RabbitMQ broker for outbox worker")
        await broker.stop()


if __name__ == "__main__":
    asyncio.run(main())
