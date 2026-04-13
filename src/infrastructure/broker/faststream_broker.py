import logging
from typing import Any

from faststream.rabbit import RabbitBroker

from src.core.interfaces.message_broker import AbstractMessageBroker

logger = logging.getLogger(__name__)


class FastStreamRabbitBroker(AbstractMessageBroker):
    """RabbitMQ adapter built on top of FastStream."""

    def __init__(self, broker: RabbitBroker):
        """Initialize the adapter.

        Args:
            broker: Configured FastStream broker instance.
        """

        self.broker = broker

    async def publish(self, routing_key: str, payload: dict[str, Any]) -> None:
        """Publish a message to RabbitMQ.

        Args:
            routing_key: Queue or routing key name.
            payload: Message body.
        """

        logger.debug("Publishing message to %s", routing_key)
        await self.broker.publish(message=payload, queue=routing_key)
