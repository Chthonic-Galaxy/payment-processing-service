import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.exc import IntegrityError

from src.api.dependencies import get_payment_service, verify_api_key
from src.api.v1.schemas import PaymentCreateRequest, PaymentResponse
from src.core.use_cases.payments import PaymentService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_payment(
    request: PaymentCreateRequest,
    service: Annotated[PaymentService, Depends(get_payment_service)],
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
):
    """Create a new payment.

    Args:
        request: Payment creation payload.
        service: Payment application service.
        idempotency_key: Idempotency key from the request header.

    Returns:
        Created payment data.
    """

    try:
        payment = await service.create_payment(
            amount=request.amount,
            currency=request.currency,
            description=request.description,
            webhook_url=request.webhook_url,
            idempotency_key=idempotency_key,
            metadata=request.metadata,
        )
        logger.info("Payment %s accepted for processing", payment.id)
        return payment
    except IntegrityError:
        logger.warning(
            "Payment creation rejected because idempotency key %s already exists",
            idempotency_key,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payment with this Idempotency-Key already exists.",
        )


@router.get("/{payment_id}/", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    service: Annotated[PaymentService, Depends(get_payment_service)],
):
    """Return payment details by ID.

    Args:
        payment_id: Payment identifier.
        service: Payment application service.

    Returns:
        Payment data.
    """

    payment = await service.get_payment(str(payment_id))
    if not payment:
        logger.warning("Payment %s not found", payment_id)
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
