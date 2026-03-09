from typing import Optional
from datetime import datetime

from database.models import User
from services.schemas import UserCreate
from services.security import hash_password



class UserFactory:
    @staticmethod
    def create_from_dto(dto: UserCreate) -> User:
        user = User(
            username=dto.username,
            email=dto.email,
            password=hash_password(dto.password),
            is_active=dto.is_active,
            is_admin=False
        )
        return user

    @staticmethod
    def create_user(
        user_id: int,
        username: str,
        email: str,
        password: str,
        is_admin: bool = False,
        is_active: bool = True
    ) -> User:
        return User(
            user_id=user_id,
            username=username,
            email=email,
            password=password,
            is_admin=is_admin,
            is_active=is_active
        )