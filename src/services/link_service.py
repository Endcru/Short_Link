from typing import Optional, Sequence
from fastapi import HTTPException, status, Depends

from database.models import Link
from services.schemas import LinkCreate, LinkInDB
from unit_of_work import UnitOfWork
from factories.link_factory import LinkFactory
from database.models import User
import random
import string

class LinkService:
    async def create_link_authorized(self, link_data: LinkCreate, user: User) -> LinkInDB:
        async with UnitOfWork() as uow:
            db_user = await uow.users.get_by_id(user.id)
            link = LinkFactory.create_for_authorized_user(link_data, db_user)
            created_link = await uow.links.create(link)
            await uow.commit()
            return LinkInDB.model_validate(created_link)
        
    async def create_link_unauthorized(self, link_data: LinkCreate) -> LinkInDB:
        async with UnitOfWork() as uow:
            link = LinkFactory.create_for_unauthorized_user(link_data)
            created_link = await uow.links.create(link)
            await uow.commit()
            return LinkInDB.model_validate(created_link)
    
    async def use_short_code(self, short_code: str) -> LinkInDB:
        async with UnitOfWork() as uow:
            link = await uow.links.get_by_short_code(short_code)
            if not link:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
            await uow.links.increment_transitions(link)
            return link.original_url
    
    async def get_link_by_short_code(self, short_code: str) -> LinkInDB:
        async with UnitOfWork() as uow:
            link = await uow.links.get_by_short_code(short_code)
            if not link:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
            return LinkInDB.model_validate(link)
    
    async def get_all_links(self, skip: int = 0, limit: int = 100) -> Sequence[LinkInDB]:
        async with UnitOfWork() as uow:
            links = await uow.links.get_all(skip, limit)

            total = await uow.links.count()
            link_dtos = [LinkInDB.model_validate(link) for link in links]

            return link_dtos, total
    
    async def check_short_code_exists(self, short_code: str) -> bool:
        async with UnitOfWork() as uow:
            link = await uow.links.get_by_short_code(short_code)
            return link is not None