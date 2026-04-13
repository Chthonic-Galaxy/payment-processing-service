from abc import ABC, abstractmethod

from src.core.entities.payment import Payment, PaymentStatus


class AbstractPaymentRepository(ABC):
    @abstractmethod
    async def create(self, payment: Payment) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, payment_id: str) -> Payment | None:
        raise NotImplementedError

    @abstractmethod
    async def update_status(self, payment_id: str, status: PaymentStatus) -> None:
        raise NotImplementedError
