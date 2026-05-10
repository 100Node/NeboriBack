import os
import uuid
import logging
import consul
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from app.core.config import settings
from app.modules.tasks.consumers import router as tasks_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Налаштування Consul ---
CONSUL_HOST = os.getenv("CONSUL_HOST", "nebori-consul")
SERVICE_NAME = "transcoding-worker"
SERVICE_ID = f"{SERVICE_NAME}-{uuid.uuid4().hex[:8]}"
SERVICE_ADDRESS = os.getenv("HOSTNAME", "nebori-transcoding-serv")

c = consul.Consul(host=CONSUL_HOST, port=8500)
# --------------------------

broker = RabbitBroker(settings.RABBITMQ_URL)
broker.include_router(tasks_router)

app = FastStream(broker)

@app.after_startup
async def register_in_consul():
    logger.info(f"Registering FastStream worker in Consul as {SERVICE_ID}...")
    c.agent.service.register(
        name=SERVICE_NAME,
        service_id=SERVICE_ID,
        address=SERVICE_ADDRESS,
        port=8000 # Порт вказуємо для консистентності реєстру
    )

@app.after_shutdown
async def deregister_from_consul():
    logger.info("Deregistering FastStream worker from Consul...")
    c.agent.service.deregister(SERVICE_ID)