import logging
from decimal import Decimal
from typing import Any

from pydantic import HttpUrl

from src.core.entities.payment import Currency, Payment
from src.core.interfaces.payments import AbstractPaymentRepository

logger = logging.getLogger(__name__)


class PaymentService:
    """Application service for payment operations."""

    def __init__(self, db_repo: AbstractPaymentRepository):
        """Initialize the service.

        Args:
            db_repo: Repository used to work with payments.
        """

        self.db_repo = db_repo

    async def create_payment(
        self,
        amount: Decimal,
        currency: Currency,
        description: str,
        webhook_url: HttpUrl,
        idempotency_key: str,
        metadata: dict[str, Any] | None = None,
    ) -> Payment:
        """Create a payment and store it in the repository.

        Args:
            amount: Payment amount.
            currency: Payment currency.
            description: Payment description.
            webhook_url: Callback URL for payment status updates.
            idempotency_key: Client-provided idempotency key.
            metadata: Optional extra payment data.

        Returns:
            Created payment entity.
        """

        logger.debug("Creating payment with idempotency key %s", idempotency_key)

        payment = Payment(
            amount=amount,
            currency=currency,
            description=description,
            webhook_url=webhook_url,
            idempotency_key=idempotency_key,
            metadata=metadata or {},
        )

        await self.db_repo.create(payment)
        logger.debug("Payment %s created", payment.id)

        return payment

    async def get_payment(self, payment_id: str) -> Payment | None:
        """Return a payment by ID.

        Args:
            payment_id: Payment identifier.

        Returns:
            Payment entity if found, otherwise `None`.
        """

        logger.debug("Fetching payment %s", payment_id)
        return await self.db_repo.get(payment_id)
