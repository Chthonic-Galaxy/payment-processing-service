from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, HttpUrl

from src.core.entities.payment import Currency, PaymentStatus


class PaymentCreateRequest(BaseModel):
    amount: Decimal
    currency: Currency
    description: str
    metadata: dict[str, Any] = {}
    webhook_url: HttpUrl


class PaymentResponse(BaseModel):
    id: UUID
    status: PaymentStatus
    created_at: datetime
    amount: Decimal
    currency: Currency
