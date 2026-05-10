import os
import uuid
import logging
import consul
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from faststream.rabbit import RabbitBroker

from app.core.config import settings, Environment
from app.modules.achievements.router import router as achievements_router
from app.modules.achievements.consumers import router as consumers_router

logger = logging.getLogger(__name__)

# --- Налаштування Consul ---
CONSUL_HOST = os.getenv("CONSUL_HOST", "nebori-consul")
SERVICE_NAME = "achievements-service"
SERVICE_ID = f"{SERVICE_NAME}-{uuid.uuid4().hex[:8]}"
SERVICE_ADDRESS = os.getenv("HOSTNAME", "nebori-achievements-serv")
SERVICE_PORT = 8000

c = consul.Consul(host=CONSUL_HOST, port=8500)
# --------------------------

broker = RabbitBroker(settings.RABBITMQ_URL)
broker.include_router(consumers_router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await broker.start()
        logger.info("RabbitMQ connected to Achievements Service")
        
        logger.info(f"Registering in Consul as {SERVICE_ID}...")
        c.agent.service.register(
            name=SERVICE_NAME,
            service_id=SERVICE_ID,
            address=SERVICE_ADDRESS,
            port=SERVICE_PORT
        )
    except Exception as e:
        logger.error(f"Failed to start services: {e}")
        # Not raising here to allow app to start even if consul is down in dev
        
    yield
    
    try:
        logger.info("Deregistering from Consul...")
        c.agent.service.deregister(SERVICE_ID)
    except Exception:
        pass
    await broker.stop()

docs_url = "/docs" if settings.ENVIRONMENT != Environment.PROD else None
redoc_url = "/redoc" if settings.ENVIRONMENT != Environment.PROD else None

app = FastAPI(
    title="Nebori Achievements Service API",
    debug=settings.DEBUG,
    docs_url=docs_url,
    redoc_url=redoc_url,
    version="0.1.0",
    openapi_url="/openapi.json" if settings.ENVIRONMENT != Environment.PROD else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(achievements_router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok", 
        "service": "achievements",
        "consul_id": SERVICE_ID
    }
