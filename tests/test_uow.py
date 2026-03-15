"""Тесты UnitOfWork."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from unit_of_work import UnitOfWork


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.flush = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_uow_creates_repositories(mock_session):
    with patch("unit_of_work.async_session_maker", return_value=mock_session):
        async with UnitOfWork() as uow:
            assert uow.users is not None
            assert uow.links is not None
            assert uow._session is mock_session
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_uow_commit(mock_session):
    with patch("unit_of_work.async_session_maker", return_value=mock_session):
        async with UnitOfWork() as uow:
            await uow.commit()
        mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_uow_flush(mock_session):
    with patch("unit_of_work.async_session_maker", return_value=mock_session):
        async with UnitOfWork() as uow:
            await uow.flush()
        mock_session.flush.assert_called_once()


@pytest.mark.asyncio
async def test_uow_rollback(mock_session):
    with patch("unit_of_work.async_session_maker", return_value=mock_session):
        async with UnitOfWork() as uow:
            await uow.rollback()
        mock_session.rollback.assert_called_once()



def test_uow_users_error():
    uow = UnitOfWork()
    with pytest.raises(RuntimeError):
        users = uow.users


def test_uow_links_error():
    uow = UnitOfWork()
    with pytest.raises(RuntimeError):
        links = uow.links


@pytest.mark.asyncio
async def test_uow_commit_error():
    uow = UnitOfWork()
    with pytest.raises(RuntimeError):
        await uow.commit()


@pytest.mark.asyncio
async def test_uow_rollback_error():
    uow = UnitOfWork()
    with pytest.raises(RuntimeError):
        await uow.rollback()


@pytest.mark.asyncio
async def test_uow_flush_error():
    uow = UnitOfWork()
    with pytest.raises(RuntimeError):
        await uow.flush()
