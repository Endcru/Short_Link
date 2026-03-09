import os

from dotenv import load_dotenv

# Суперподробное логирование для отладки
import logging
logging.basicConfig(level=logging.DEBUG)

# Загрузка переменных из .env файла
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")