from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.core.interfaces.payments import AbstractPaymentRepository
from src.core.use_cases.payments import PaymentService
from src.infrastructure.database.connection import get_db_session
from src.infrastructure.database.repositories.payments import SQLAlchemyPaymentRepository

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    if api_key != settings.app_api_key.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return api_key


def get_payment_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AbstractPaymentRepository:
    return SQLAlchemyPaymentRepository(session)


def get_payment_service(
    payment_repo: Annotated[AbstractPaymentRepository, Depends(get_payment_repository)],
) -> PaymentService:
    return PaymentService(db_repo=payment_repo)
