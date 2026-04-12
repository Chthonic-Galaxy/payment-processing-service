from abc import ABC, abstractmethod
from typing import Any


class AbstractMessageBroker(ABC):
    @abstractmethod
    async def publish(self, routing_key: str, payload: dict[str, Any]) -> None:
        raise NotImplementedError
