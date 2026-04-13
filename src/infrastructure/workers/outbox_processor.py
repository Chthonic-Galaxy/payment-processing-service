import asyncio
import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.interfaces.message_broker import AbstractMessageBroker
from src.infrastructure.database.models import Outbox

logger = logging.getLogger(__name__)


class OutboxProcessor:
    """Background worker that publishes pending outbox messages."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        broker: AbstractMessageBroker,
        batch_size: int = 50,
        sleep_interval: float = 1.0,
    ):
        """Initialize the processor.

        Args:
            session_factory: Database session factory.
            broker: Message broker adapter.
            batch_size: Maximum number of messages per iteration.
            sleep_interval: Delay between iterations in seconds.
        """

        self.session_factory = session_factory
        self.broker = broker
        self.batch_size = batch_size
        self.sleep_interval = sleep_interval
        self._running = False

    async def start(self) -> None:
        """Start the processing loop."""

        self._running = True
        logger.info("Outbox processor started")
        while self._running:
            try:
                await self._process_batch()
            except Exception:
                logger.exception("Outbox batch processing failed")

            await asyncio.sleep(self.sleep_interval)

    def stop(self) -> None:
        """Stop the processing loop."""

        self._running = False
        logger.info("Outbox processor stop requested")

    async def _process_batch(self) -> None:
        """Process a single batch of pending outbox messages."""

        async with self.session_factory() as session:
            stmt = (
                select(Outbox)
                .where(Outbox.processed.is_(False))
                .limit(self.batch_size)
                .with_for_update(skip_locked=True)
            )
            messages = (await session.execute(stmt)).scalars().all()

            if not messages:
                return

            logger.info("Processing %s outbox messages", len(messages))
            processed_ids = []
            for msg in messages:
                try:
                    await self.broker.publish(routing_key=msg.routing_key, payload=msg.payload)
                    processed_ids.append(msg.id)
                except Exception:
                    logger.exception("Failed to publish outbox message %s", msg.id)

            if processed_ids:
                update_stmt = (
                    update(Outbox).where(Outbox.id.in_(processed_ids)).values(processed=True)
                )
                await session.execute(update_stmt)
                await session.commit()
                logger.info("Marked %s outbox messages as processed", len(processed_ids))
