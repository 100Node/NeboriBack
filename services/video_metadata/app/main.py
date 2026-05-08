import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from faststream.rabbit import RabbitBroker

from app.core.config import settings, Environment
from app.modules.videos.router import router as videos_router
from app.modules.videos.consumers import router as consumers_router

logger = logging.getLogger(__name__)

broker = RabbitBroker(settings.RABBITMQ_URL)
broker.include_router(consumers_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await broker.start()
        logger.info("RabbitMQ connected to Metadata Service")
        print("RabbitMQ connected to Metadata Service")
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        raise
    yield
    await broker.stop()


docs_url = "/docs" if settings.ENVIRONMENT != Environment.PROD else None
redoc_url = "/redoc" if settings.ENVIRONMENT != Environment.PROD else None

app = FastAPI(
    title="Nebori Metadata Service API",
    debug=settings.DEBUG,
    docs_url=docs_url,
    redoc_url=redoc_url,
    version="0.1.0",
    openapi_url="/openapi.json" if settings.ENVIRONMENT != Environment.PROD else None,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(videos_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": "video_metadata"
    }