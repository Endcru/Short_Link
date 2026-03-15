import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest
from datetime import datetime, timedelta, timezone
from database.models import Link
from services.link_service import LinkService
from services.schemas import LinkCreate
from unit_of_work import UnitOfWork

@pytest.mark.asyncio
async def test_delete_expired_links(client):
    async with UnitOfWork() as uow:
        admin = await uow.users.get_by_username("admin")
    assert admin is not None
    now = datetime.now(timezone.utc)
    past = now - timedelta(hours=1)
    link = Link(original_url="https://expired.com/", short_code="expired_link", project=None, transitions=0, last_transition_at=None, expires_at=past, user_id=admin.id)
    async with UnitOfWork() as uow:
        await uow.links.create(link)
        await uow.commit()
    async with UnitOfWork() as uow:
        found = await uow.links.get_by_short_code("expired_link")
    assert found is not None
    service = LinkService()
    deleted = await service.delete_expired_links()
    assert deleted == 1
    async with UnitOfWork() as uow:
        found = await uow.links.get_by_short_code("expired_link")
    assert found is None
