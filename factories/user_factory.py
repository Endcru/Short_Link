from typing import Optional
from datetime import datetime

from database.models import User


class UserFactory:
    @staticmethod
    def create_user(
        user_id: int,
        name: str,
        last_name: str = None,
        username: str = None,
        is_active: bool = True
    ) -> User:
        return User(
            user_id=user_id,
            is_active=is_active,
            name=name,
            last_name = last_name,
            username = username
        )