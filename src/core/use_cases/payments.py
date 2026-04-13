from decimal import Decimal
from typing import Any

from pydantic import HttpUrl

from src.core.entities.payment import Currency, Payment
from src.core.interfaces.payments import AbstractPaymentRepository


class PaymentService:
    def __init__(self, db_repo: AbstractPaymentRepository):
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

        payment = Payment(
            amount=amount,
            currency=currency,
            description=description,
            webhook_url=webhook_url,
            idempotency_key=idempotency_key,
            metadata=metadata or {},
        )

        await self.db_repo.create(payment)

        return payment

    async def get_payment(self, payment_id: str) -> Payment | None:
        return await self.db_repo.get(payment_id)
