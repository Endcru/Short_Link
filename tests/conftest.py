import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["USE_REDIS"] = "0"  # InMemory для тестов; USE_REDIS=1 для тестов с Redis
import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.database import Base, engine
from main import app


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    original_schemas = {name: t.schema for name, t in Base.metadata.tables.items()}
    for table in Base.metadata.tables.values():
        table.schema = None
    Base.metadata.create_all(engine)
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    finally:
        for name, table in Base.metadata.tables.items():
            table.schema = original_schemas.get(name)


@pytest.fixture(scope="module")
def client():
    for t in Base.metadata.tables.values():
        t.schema = None
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(create_tables())
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    r = client.post("/user/login", data={"username": "admin", "password": "password"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
