from faststream.rabbit import RabbitBroker, RabbitQueue

from src.config import settings

broker = RabbitBroker(settings.broker.url)

main_queue = RabbitQueue(
    name="payments.new",
    routing_key="payments.new",
    arguments={
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": "payments.dlq",
    },
)
