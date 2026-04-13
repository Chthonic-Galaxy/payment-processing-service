from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from src.core.entities.payment import Currency, PaymentStatus


class PaymentCreateRequest(BaseModel):
    """Request body for payment creation."""

    amount: Decimal
    currency: Currency
    description: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    webhook_url: HttpUrl


class PaymentResponse(BaseModel):
    """Response body with payment details."""

    id: UUID
    status: PaymentStatus
    created_at: datetime
    amount: Decimal
    currency: Currency
