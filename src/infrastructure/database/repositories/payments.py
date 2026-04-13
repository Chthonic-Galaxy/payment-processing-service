import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.entities.payment import Payment as PaymentEntity
from src.core.entities.payment import PaymentStatus
from src.core.interfaces.payments import AbstractPaymentRepository
from src.infrastructure.database.models import Outbox
from src.infrastructure.database.models import Payment as PaymentModel
from src.utils import utc_now

logger = logging.getLogger(__name__)


class SQLAlchemyPaymentRepository(AbstractPaymentRepository):
    """SQLAlchemy implementation of the payment repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.

        Args:
            session: Active database session.
        """

        self.session = session

    @staticmethod
    def __mapper_dao_to_dm(dao: PaymentModel) -> PaymentEntity:
        """Convert ORM payment model to a domain entity.

        Args:
            dao: ORM payment model.

        Returns:
            Domain payment entity.
        """

        data = {
            "id": dao.id,
            "amount": dao.amount,
            "currency": dao.currency,
            "description": dao.description,
            "metadata": dao.payment_metadata,
            "status": dao.status,
            "idempotency_key": dao.idempotency_key,
            "webhook_url": dao.webhook_url,
            "created_at": dao.created_at,
            "processed_at": dao.processed_at,
        }
        return PaymentEntity.model_validate(data)

    @staticmethod
    def __mapper_dm_to_dao(dm: PaymentEntity) -> PaymentModel:
        """Convert a domain entity to an ORM payment model.

        Args:
            dm: Domain payment entity.

        Returns:
            ORM payment model.
        """

        data = dm.model_dump()
        data["payment_metadata"] = data.pop("metadata")
        data["webhook_url"] = str(data["webhook_url"])
        return PaymentModel(**data)

    async def create(self, payment: PaymentEntity) -> None:
        """Persist a payment and create an outbox message.

        Args:
            payment: Payment entity to store.
        """

        outbox_payload = payment.model_dump(mode="json")

        self.session.add(self.__mapper_dm_to_dao(payment))

        self.session.add(
            Outbox(
                routing_key="payments.new",
                payload=outbox_payload,
            )
        )

        await self.session.flush()
        logger.debug("Payment %s saved and added to outbox", payment.id)

    async def get(self, payment_id: str) -> PaymentEntity | None:
        """Return a payment by ID.

        Args:
            payment_id: Payment identifier.

        Returns:
            Payment entity if found, otherwise `None`.
        """

        stmt = select(PaymentModel).where(PaymentModel.id == payment_id)
        payment = (await self.session.execute(stmt)).scalar_one_or_none()

        if not payment:
            logger.debug("Payment %s was not found in the database", payment_id)
            return payment

        logger.debug("Payment %s loaded from the database", payment_id)
        return self.__mapper_dao_to_dm(payment)

    async def update_status(self, payment_id: str, status: PaymentStatus) -> None:
        """Update payment status and processing time.

        Args:
            payment_id: Payment identifier.
            status: New payment status.
        """

        stmt = (
            update(PaymentModel)
            .where(PaymentModel.id == payment_id)
            .values(status=status, processed_at=utc_now())
        )
        await self.session.execute(stmt)
        logger.info("Payment %s status updated to %s", payment_id, status.value)
