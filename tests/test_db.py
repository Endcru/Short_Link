import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock, MagicMock, patch
from database.database import get_session, init_db, Base
from database.models import User, Link
from services.security import hash_password, check_password
from conftest import db_session


def test_user_creation(db_session):

    hashed = hash_password("test_password")
    user = User(username="test_user", email="test_user@mail.com", password=hashed, is_active=True, is_admin=False)
    db_session.add(user)
    db_session.commit()
    result = db_session.execute(select(User).where(User.username == "test_user")).scalars().first()
    assert result is not None
    assert result.username == "test_user"
    assert result.email == "test_user@mail.com"
    assert check_password("test_password", result.password)
    result.deactivate()
    assert result.is_active == False
    result.activate()
    assert result.is_active == True
    assert result.__repr__() == "<User(id=1, username='test_user', email='test_user@mail.com')>"

def test_link_creation(db_session):

    link = Link(original_url="https://www.youtube.com/", short_code="youtube", user_id=1, project="youtube_project", transitions=0, last_transition_at=None, expires_at=None)
    db_session.add(link)
    db_session.commit()
    result = db_session.execute(select(Link).where(Link.short_code == "youtube")).scalars().first()
    assert result is not None
    assert result.original_url == "https://www.youtube.com/"
    assert result.short_code == "youtube"
    assert result.user_id == 1
    assert result.project == "youtube_project"
    assert result.transitions == 0
    assert result.last_transition_at is None
    assert result.expires_at is None
    assert result.__repr__() == "<Link(id=1, short_code='youtube', original_url='https://www.youtube.com/')>"


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_get_session(mock_session):
    with patch("database.database.async_session_maker") as mock_maker:
        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=None)
        mock_maker.return_value = mock_cm
        gen = get_session()
        session = await gen.__anext__()
        assert session is mock_session
        with pytest.raises(StopAsyncIteration):
            await gen.__anext__()
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_init_db_creates_admin(mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    with patch("database.database.async_session_maker") as mock_maker:
        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=None)
        mock_maker.return_value = mock_cm
        with patch("database.database.hash_password") as mock_hash:
            mock_hash.return_value = "hashed_password"
            await init_db()
            mock_session.add.assert_called_once()
            added_admin = mock_session.add.call_args[0][0]
            assert isinstance(added_admin, User)
            assert added_admin.username == "admin"
            assert added_admin.email == "admin@mail.com"
            assert added_admin.is_admin is True
            mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_init_db_skips_admin(mock_session):
    now = datetime.now(timezone.utc)
    existing_admin = User(id=1, username="admin", email="admin@mail.com", password="hashed_password", is_admin=True, is_active=True, created_at=now, updated_at=now)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_admin
    mock_session.execute.return_value = mock_result
    with patch("database.database.async_session_maker") as mock_maker:
        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=None)
        mock_maker.return_value = mock_cm
        await init_db()
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()