from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator

from app.auth.router import router as router_auth
from app.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Управление жизненным циклом приложения."""
    logger.info("Инициализация приложения...")
    yield
    logger.info("Завершение работы приложения...")


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
