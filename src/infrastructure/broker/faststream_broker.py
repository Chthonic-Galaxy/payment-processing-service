from typing import Any

from faststream.rabbit import RabbitBroker

from src.core.interfaces.message_broker import AbstractMessageBroker


class FastStreamRabbitBroker(AbstractMessageBroker):
    def __init__(self, broker: RabbitBroker):
        self.broker = broker

    async def publish(self, routing_key: str, payload: dict[str, Any]) -> None:
        await self.broker.publish(message=payload, queue=routing_key)
