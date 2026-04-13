import asyncio
import logging

from src.infrastructure.broker.consumer import broker
from src.infrastructure.broker.faststream_broker import FastStreamRabbitBroker
from src.infrastructure.database.connection import async_session_factory
from src.infrastructure.workers.outbox_processor import OutboxProcessor

logging.basicConfig(level=logging.INFO)


async def main():
    await broker.connect()

    rabbit_adapter = FastStreamRabbitBroker(broker)

    processor = OutboxProcessor(session_factory=async_session_factory, broker=rabbit_adapter)

    try:
        await processor.start()
    finally:
        await broker.stop()


if __name__ == "__main__":
    asyncio.run(main())
