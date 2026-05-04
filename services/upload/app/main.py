from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from faststream.rabbit import RabbitBroker

from app.core.config import settings, Environment
from app.modules.videos.router import router as videos_router

broker = RabbitBroker(settings.RABBITMQ_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.connect()
    print("RabbitMQ connected to Upload Service")
    
    yield
    
    await broker.stop()


docs_url = "/docs" if settings.ENVIRONMENT != Environment.PROD else None
redoc_url = "/redoc" if settings.ENVIRONMENT != Environment.PROD else None

app = FastAPI(
    title="upload_video API",
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
        "service": "upload_video"
    }