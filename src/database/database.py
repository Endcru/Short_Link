from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select
from services.security import hash_password
from config import ADMIN_PASSWORD, DATABASE_URL

class Base(DeclarativeBase):
    __table_args__ = {"schema": "short-link"}

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with async_session_maker() as session:
        from database.models import User
        result = await session.execute(
            select(User).where(User.username == "admin")
        )
        admin = result.scalar_one_or_none()
        if not admin: # Если нет админа, создаем его
            admin = User(
                username="admin",
                email="admin@mail.com",
                password=hash_password(ADMIN_PASSWORD),
                is_admin=True,
                is_active=True,
            )
            session.add(admin)
            await session.commit()