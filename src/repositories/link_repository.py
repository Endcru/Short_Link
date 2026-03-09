from typing import Optional, Sequence
from sqlalchemy import select, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Link
from repositories.base import BaseRepository
from datetime import datetime, timezone


class LinkRepository(BaseRepository[Link]):

    def __init__(self, session: AsyncSession):
        super().__init__(Link, session)

    async def get_by_short_code(self, short_code: str) -> Optional[Link]:
            stmt = select(Link).where(Link.short_code == short_code)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        
    async def get_by_original_url(self, original_url: str, user_id: int ) -> Sequence[Link]:
            stmt = select(Link).where(Link.original_url == original_url, Link.user_id == user_id)
            result = await self.session.execute(stmt)
            return result.scalars().all()

    async def get_by_original_url_unauthorized(self, original_url: str) -> Sequence[Link]:
            stmt = select(Link).where(Link.original_url == original_url, Link.user_id.is_(None))
            result = await self.session.execute(stmt)
            return result.scalars().all()
        
    async def get_by_project(self, project: str, user_id: int) -> Sequence[Link]:
            stmt = select(Link).where(Link.project == project, Link.user_id == user_id)
            result = await self.session.execute(stmt)
            return result.scalars().all()
    
    async def increment_transitions(self, link: Link):
        link.transitions += 1
        link.last_transition_at = datetime.now(timezone.utc)
        await self.session.commit()

    async def delete_expired_links(self) -> int:
        """Delete links where expires_at has passed. Returns count of deleted links."""
        now = datetime.now(timezone.utc)
        stmt = delete(Link).where(Link.expires_at.isnot(None), Link.expires_at <= now)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount or 0    