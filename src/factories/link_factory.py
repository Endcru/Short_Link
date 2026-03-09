from typing import Optional
from datetime import datetime

from database.models import User, Link
from services.schemas import LinkCreate
import random
import string
from fastapi import HTTPException, status
from nanoid import generate

@staticmethod
def generate_random_short_code() -> str:
    return generate(size=8)

class LinkFactory:

    @staticmethod
    def create_for_unauthorized_user(dto: LinkCreate) -> Link:
        link = Link(
            original_url=dto.original_url,
            short_code=generate_random_short_code(),
            user_registred=False,
            project=None,
            transitions=0,
            last_transition_at=None,
            expires_at=dto.expires_at,
            user=None
        )
        return link
    
    @staticmethod
    def create_for_authorized_user(dto: LinkCreate, user: User) -> Link:
        link = Link(
            original_url=dto.original_url,
            short_code=dto.custom_alias if dto.custom_alias else generate_random_short_code(),
            user_registred=True,
            project=dto.project,
            transitions=0,
            last_transition_at=None,
            expires_at=dto.expires_at,
            user=user
        )
        return link
    
    @staticmethod
    def create_link(
        original_url: str,
        short_code: str,
        user_registred: bool = False,
        project: str = None,
        transitions: int = 0,
        last_transition_at: datetime = None,
        expires_at: Optional[datetime] = None,
        user: Optional["User"] = None
    ) -> Link:
        return Link(
            original_url=original_url,
            short_code=short_code,
            user_registred=user_registred,
            project=project,
            transitions=transitions,
            last_transition_at=last_transition_at,
            expires_at=expires_at,
            user=user
        )