from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.exc import IntegrityError

from src.api.dependencies import get_payment_service, verify_api_key
from src.api.v1.schemas import PaymentCreateRequest, PaymentResponse
from src.core.use_cases.payments import PaymentService

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
    try:
        payment = await service.create_payment(
            amount=request.amount,
            currency=request.currency,
            description=request.description,
            webhook_url=request.webhook_url,
            idempotency_key=idempotency_key,
            metadata=request.metadata,
        )
        return payment
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payment with this Idempotency-Key already exists.",
        )


@router.get("/{payment_id}/", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    service: Annotated[PaymentService, Depends(get_payment_service)],
):
    payment = await service.get_payment(str(payment_id))
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
