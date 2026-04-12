import asyncio

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.interfaces.message_broker import AbstractMessageBroker
from src.infrastructure.database.models import Outbox


class OutboxProcessor:
    def __init__(
        self,
        session: AsyncSession,
        broker: AbstractMessageBroker,
        batch_size: int = 50,
        sleep_interval: float = 1.0,
    ):
        self.session = session
        self.broker = broker
        self.batch_size = batch_size
        self.sleep_interval = sleep_interval
        self._running = False

    async def start(self) -> None:
        self._running = True
        while self._running:
            try:
                await self._process_batch()
            except Exception:
                pass

            await asyncio.sleep(self.sleep_interval)

    def stop(self) -> None:
        self._running = False

    async def _process_batch(self) -> None:
        stmt = (
            select(Outbox)
            .where(Outbox.processed == False)
            .limit(self.batch_size)
            .with_for_update(skip_locked=True)
        )
        messages = (await self.session.execute(stmt)).scalars().all()

        if not messages:
            return

        processed_ids = []
        for msg in messages:
            try:
                await self.broker.publish(routing_key=msg.routing_key, payload=msg.payload)
                processed_ids.append(msg.id)
            except Exception:
                pass

        if processed_ids:
            update_stmt = (
                update(Outbox).where(Outbox.id.in_(processed_ids)).values(processed_ids=True)
            )
            await self.session.execute(update_stmt)
