from abc import ABC, abstractmethod
from typing import Any


class AbstractMessageBroker(ABC):
    """Message broker contract."""

    @abstractmethod
    async def publish(self, routing_key: str, payload: dict[str, Any]) -> None:
        """Publish a message to a routing key."""

        raise NotImplementedError
