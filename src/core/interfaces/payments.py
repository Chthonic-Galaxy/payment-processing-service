from abc import ABC, abstractmethod

from src.core.entities.payment import Payment, PaymentStatus


class AbstractPaymentRepository(ABC):
    """Payment repository contract."""

    @abstractmethod
    async def create(self, payment: Payment) -> None:
        """Persist a new payment."""

        raise NotImplementedError

    @abstractmethod
    async def get(self, payment_id: str) -> Payment | None:
        """Return a payment by ID."""

        raise NotImplementedError

    @abstractmethod
    async def update_status(self, payment_id: str, status: PaymentStatus) -> None:
        """Update the current payment status."""

        raise NotImplementedError
