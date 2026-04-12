from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.entities.payment import Payment as PaymentEntity
from src.core.interfaces.payments import AbstractPaymentRepository
from src.infrastructure.database.models import Outbox
from src.infrastructure.database.models import Payment as PaymentModel


class SLQAlchemyPaymentRepository(AbstractPaymentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def __mapper_dao_to_dm(dao: PaymentModel) -> PaymentEntity:
        return PaymentEntity.model_validate(dao)

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

    async def get(self, payment_id: str) -> PaymentEntity | None:
        stmt = select(PaymentModel).where(PaymentModel.id == payment_id)
        payment = (await self.session.execute(stmt)).scalar_one_or_none()

        if not payment:
            return payment

        return self.__mapper_dao_to_dm(payment)
