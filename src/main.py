import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn
import logging

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from redis import asyncio as aioredis

from database.database import init_db
from routers import user, link
from services.link_service import LinkService
from config import DELETE_INTERVAL_SECONDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def expired_links_delete_task():
    link_service = LinkService()
    while True:
        try:
            deleted = await link_service.delete_expired_links()
            if deleted > 0:
                logger.info(f"Удалено истекших ссылок: {deleted}")
            await asyncio.sleep(DELETE_INTERVAL_SECONDS)
        except asyncio.CancelledError:
            logger.info("Остановка задачи удаления истекших ссылок")
            raise
        except (TimeoutError, ConnectionError) as e:
            logger.warning(f"Ошибка при удалении истекших ссылок: {e}")
            await asyncio.sleep(DELETE_INTERVAL_SECONDS)
        except Exception as e:
            logger.exception(f"Ошибка при удалении истекших ссылок: {e}")
            await asyncio.sleep(DELETE_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup / Запуск
    print("Инициализация БД...")
    await init_db()
    print("БД инициализирована")

    print("Инициализация Redis...")
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    print("Redis инициализирован")

    cleanup_task = asyncio.create_task(expired_links_delete_task())
    logger.info("Запуск удаления истёкших ссылок")

    yield

    # Shutdown / Завершение
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    print("Завершение работы...")

# Create FastAPI application / Создать FastAPI приложение
app = FastAPI(
    title="Short Link Server",
    description="""
    Server for Short Link service
    """,
    version="1.0.0",
    lifespan=lifespan
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error for request {await request.body()}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "bad request"}
    )


# Include routers / Подключить роутеры
app.include_router(user.router)
app.include_router(link.router)


@app.get(
    "/",
    summary="Root endpoint / Корневой эндпоинт",
    description="Get API information / Получить информацию об API"
)
async def root():
    """
    Root endpoint with architecture overview
    Корневой эндпоинт с обзором архитектуры
    """
    return {
        "message": "Short Link service",
    }


@app.get(
    "/health",
    summary="Health check / Проверка здоровья",
    description="Check if API is running / Проверить работу API"
)
async def health():
    """Health check endpoint / Эндпоинт проверки здоровья"""
    return {
        "status": "healthy / здоров",
        "database": "connected / подключена",
        "architecture": "DDD with async SQLAlchemy 2.0"
    }


if __name__ == "__main__":
    print("""

    Docs: http://localhost:8008/docs
    ReDoc: http://localhost:8008/redoc

    """)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8008,
        reload=True,
        log_level="info"
    )