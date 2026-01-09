import asyncio

import contextlib
from contextlib import asynccontextmanager
from loguru import logger

from collections.abc import AsyncGenerator

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from app.auth.router import router as router_auth
from app.health import router as health_router
from app.health import check_database_connection, database_connection_gauge
from app.dao.database import async_session_maker


async def db_healthcheck_loop():
    while True:
        logger.info("check_database_connection")
        try:
            async with async_session_maker() as session:
                await check_database_connection(session)
        except Exception as e:
            logger.error(f"DB background healthcheck failed: {e}")
            database_connection_gauge.set(0)

        await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Управление жизненным циклом приложения."""
    logger.info("Инициализация приложения...")
    try:
        task = asyncio.create_task(db_healthcheck_loop())
        yield
        logger.info("Завершение работы приложения...")
    finally:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


def create_app() -> FastAPI:
    """
    Создание и конфигурация FastAPI приложения.

    Returns:
        Сконфигурированное приложение FastAPI
    """
    app = FastAPI(
        title="FastAPI Starter Build",
        description=(
            "Starter build with integrated SQLAlchemy 2 for developing FastAPI applications with advanced "
        ),
        version="1.0.0",
        lifespan=lifespan,
    )

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Монтирование статических файлов
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # Регистрация роутеров
    register_routers(app)

    # Настройка Prometheus мониторинга
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app)

    return app


def register_routers(app: FastAPI) -> None:
    """Регистрация роутеров приложения."""
    # Корневой роутер
    root_router = APIRouter()

    @root_router.get("/", tags=["root"])
    def home_page() -> dict[str, str]:
        return {"message": "Добро пожаловать!"}

    # Подключение роутеров
    app.include_router(root_router, tags=["root"])
    app.include_router(router_auth, prefix="/auth", tags=["Auth"])
    app.include_router(health_router, tags=["Health"])


# Создание экземпляра приложения
app = create_app()
