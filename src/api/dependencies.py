import logging
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
logger = logging.getLogger(__name__)


def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Validate the API key from the request header.

    Args:
        api_key: API key from the `X-API-Key` header.

    Returns:
        Validated API key value.

    Raises:
        HTTPException: If the API key is invalid.
    """

    if api_key != settings.app_api_key.get_secret_value():
        logger.warning("API key validation failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return api_key


def get_payment_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AbstractPaymentRepository:
    """Create a payment repository for the current request."""

    return SQLAlchemyPaymentRepository(session)


def get_payment_service(
    payment_repo: Annotated[AbstractPaymentRepository, Depends(get_payment_repository)],
) -> PaymentService:
    """Create a payment service for the current request."""

    return PaymentService(db_repo=payment_repo)
