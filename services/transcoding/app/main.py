import logging
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from app.core.config import settings
from app.modules.tasks.consumers import router as tasks_router

logging.basicConfig(level=logging.INFO)

broker = RabbitBroker(settings.RABBITMQ_URL)

broker.include_router(tasks_router)

app = FastStream(broker)