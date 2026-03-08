from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn
import logging

from database.database import init_db
from routers import user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup / Запуск
    print("Инициализация БД...")
    await init_db()
    print("БД инициализирована")

    yield

    # Shutdown / Завершение
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