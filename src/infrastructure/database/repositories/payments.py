from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.entities.payment import Payment as PaymentEntity
from src.core.entities.payment import PaymentStatus
from src.core.interfaces.payments import AbstractPaymentRepository
from src.infrastructure.database.models import Outbox
from src.infrastructure.database.models import Payment as PaymentModel
from src.utils import utc_now


class SQLAlchemyPaymentRepository(AbstractPaymentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def __mapper_dao_to_dm(dao: PaymentModel) -> PaymentEntity:
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
        data = dm.model_dump()
        data["payment_metadata"] = data.pop("metadata")
        data["webhook_url"] = str(data["webhook_url"])
        return PaymentModel(**data)

    async def create(self, payment: PaymentEntity) -> None:
        outbox_payload = payment.model_dump(mode="json")

        self.session.add(self.__mapper_dm_to_dao(payment))

        # Outbox-Pattern
        self.session.add(
            Outbox(
                routing_key="payments.new",
                payload=outbox_payload,
            )
        )

        await self.session.flush()

    async def get(self, payment_id: str) -> PaymentEntity | None:
        stmt = select(PaymentModel).where(PaymentModel.id == payment_id)
        payment = (await self.session.execute(stmt)).scalar_one_or_none()

        if not payment:
            return payment

        return self.__mapper_dao_to_dm(payment)

    async def update_status(self, payment_id: str, status: PaymentStatus) -> None:
        stmt = (
            update(PaymentModel)
            .where(PaymentModel.id == payment_id)
            .values(status=status, processed_at=utc_now())
        )
        await self.session.execute(stmt)
