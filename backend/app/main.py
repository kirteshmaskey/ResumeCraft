"""
ResumeCraft — FastAPI Application Factory.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.core.redis import init_redis, close_redis
from app.core.database import engine, Base
import app.core.models  # noqa: F401 — register all ORM models with Base.metadata
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    generic_exception_handler,
)
from app.api.templates import router as templates_router
from app.api.generation import router as generation_router

settings = get_settings()
logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    # ── Startup ──────────────────────────────────────────────────────
    setup_logging()
    logger.info("Starting ResumeCraft v%s [%s]", settings.APP_VERSION, settings.ENVIRONMENT)

    # Create all database tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified / created")

    await init_redis()
    logger.info("Redis connection pool initialized")

    yield

    # ── Shutdown ─────────────────────────────────────────────────────
    logger.info("Shutting down ResumeCraft...")
    await close_redis()
    logger.info("All connections closed. Goodbye.")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-powered resume creation and optimization platform",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ── CORS Middleware ──────────────────────────────────────────────
    allow_origins = list(settings.ALLOWED_ORIGINS)
    if settings.DEBUG:
        for origin in ["http://localhost:4200", "http://127.0.0.1:4200"]:
            if origin not in allow_origins:
                allow_origins.append(origin)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception Handlers ───────────────────────────────────────────
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # ── Routers ──────────────────────────────────────────────────────
    from app.api.auth import router as auth_router
    app.include_router(
        auth_router, prefix="/api/v1/auth", tags=["Authentication"]
    )
    app.include_router(
        templates_router, prefix="/api/v1/templates", tags=["Templates"]
    )
    app.include_router(
        generation_router, prefix="/api/v1/generation", tags=["Generation"]
    )

    # ── Health Check ─────────────────────────────────────────────────
    @app.get("/health", tags=["System"])
    async def health_check():
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }

    # ── Public Config ───────────────────────────────────────────────
    @app.get("/api/v1/config", tags=["System"])
    async def get_public_config():
        """Expose public configuration to the frontend."""
        return {
            "appName": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
        }

    return app


# Uvicorn entry point
app = create_app()
