from typing import Optional, Sequence
from fastapi import HTTPException, status, Depends

from database.models import User
from services.schemas import UserCreate, UserUpdate, UserInDB
from unit_of_work import UnitOfWork
from factories.user_factory import UserFactory
from services.security import check_password, create_access_token
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from services.security import KEY, ALG

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    try:
        payload = jwt.decode(token, KEY, algorithms=[ALG])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    async with UnitOfWork() as uow:
        user = await uow.users.get_by_id(int(user_id))
        if not user:
            raise HTTPException(status_code=401)
        return UserInDB.model_validate(user)

class UserService:
    async def login(self, username: str, password: str) -> str:
        async with UnitOfWork() as uow:
            user = await uow.users.get_by_username(username)

            if not user or not check_password(password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )

            return create_access_token(
                data={"sub": str(user.id)}
            )

    async def create_user(self, user_data: UserCreate) -> UserInDB:
        async with UnitOfWork() as uow:
            if await uow.users.username_exists(user_data.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Username '{user_data.username}' already exists / Имя пользователя уже существует"
                )

            if await uow.users.email_exists(user_data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email '{user_data.email}' already exists / Email уже существует"
                )

            user = UserFactory.create_from_dto(user_data)

            created_user = await uow.users.create(user)

            await uow.commit()

            return UserInDB.model_validate(created_user)

    async def get_user(self, user_id: int) -> UserInDB:
        async with UnitOfWork() as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {user_id} not found / Пользователь с ID {user_id} не найден"
                )

            return UserInDB.model_validate(user)

    async def get_user_by_username(self, username: str) -> UserInDB:
        async with UnitOfWork() as uow:
            user = await uow.users.get_by_username(username)

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User '{username}' not found / Пользователь '{username}' не найден"
                )

            return UserInDB.model_validate(user)

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> tuple[Sequence[UserInDB], int]:
        async with UnitOfWork() as uow:
            if active_only:
                users = await uow.users.get_active_users(skip, limit)
            else:
                users = await uow.users.get_all(skip, limit)

            total = await uow.users.count()

            # Convert to DTOs / Конвертировать в DTO
            user_dtos = [UserInDB.model_validate(user) for user in users]

            return user_dtos, total

    async def update_user(self, user_id: int, user_data: UserUpdate) -> UserInDB:
        async with UnitOfWork() as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {user_id} not found / Пользователь с ID {user_id} не найден"
                )

            update_data = user_data.model_dump(exclude_unset=True)

            if "username" in update_data:
                if await uow.users.username_exists(update_data["username"], exclude_id=user_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Username '{update_data['username']}' already exists / Имя уже существует"
                    )

            if "email" in update_data:
                if await uow.users.email_exists(update_data["email"], exclude_id=user_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Email '{update_data['email']}' already exists / Email уже существует"
                    )

            updated_user = await uow.users.update(user_id, **update_data)

            await uow.commit()

            return UserInDB.model_validate(updated_user)

    async def delete_user(self, user_id: int) -> None:

        async with UnitOfWork() as uow:
            if not await uow.users.exists(user_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {user_id} not found / Пользователь с ID {user_id} не найден"
                )

            await uow.users.delete(user_id)

            await uow.commit()

    async def search_users(self, search_term: str, skip: int = 0, limit: int = 100) -> Sequence[UserInDB]:
        async with UnitOfWork() as uow:
            users = await uow.users.search_users(search_term, skip, limit)
            return [UserInDB.model_validate(user) for user in users]