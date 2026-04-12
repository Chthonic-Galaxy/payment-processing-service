from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from src.core.utils import utc_now, uuid_v7


class Currency(StrEnum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Payment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid_v7)

    amount: Decimal = Field(..., gt=Decimal("0.00"))
    currency: Currency
    description: str = Field(..., max_length=255)

    metadata: dict[str, Any] = Field(default_factory=dict)

    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    idempotency_key: str = Field(..., max_length=128)
    webhook_url: HttpUrl

    created_at: datetime = Field(default_factory=utc_now)
    procecssed_at: datetime | None = None

    def mark_as_succeeded(self) -> None:
        self.status = PaymentStatus.SUCCEEDED
        self.procecssed_at = utc_now()

    def mark_as_failed(self) -> None:
        self.status = PaymentStatus.FAILED
        self.procecssed_at = utc_now()
