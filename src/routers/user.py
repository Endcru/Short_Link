from typing import Optional
from fastapi import APIRouter, status, Query, Depends, HTTPException
from services.schemas import UserCreate, UserUpdate, UserResponse, UserList
from services.user_service import UserService
from services.user_service import get_current_user
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database.models import User

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "User not found / Пользователь не найден"}}
)


user_service = UserService()

@router.post("/login")
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
):
    token = await UserService().login(
        username=form.username,
        password=form.password
    )
    return {"access_token": token, "token_type": "bearer"}

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user / Создать пользователя",
    description="Create a new user with unique username and email / Создать пользователя с уникальным именем и email"
)
async def create_user(user_data: UserCreate) -> UserResponse:
    user = await user_service.create_user(user_data)
    return UserResponse.model_validate(user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID / Получить пользователя по ID",
    description="Retrieve user information by ID / Получить информацию о пользователе по ID"
)
async def get_user(user_id: int, current_user: User = Depends(get_current_user)) -> UserResponse:
    if current_user.is_admin:
        user = await user_service.get_user(user_id)
        return UserResponse.model_validate(user)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied, should be admin / Нет доступа, только для админа"
        )

@router.get(
    "/currentUser/",
    response_model=UserResponse,
    summary="Получить пользователя по Токену",
    description="Получить информацию о пользователе по токену"
)
async def current_user(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.get(
    "/username/{username}",
    response_model=UserResponse,
    summary="Get user by username / Получить пользователя по имени",
    description="Retrieve user information by username / Получить информацию по имени пользователя"
)
async def get_user_by_username(username: str, current_user: User = Depends(get_current_user)) -> UserResponse:
    if current_user.is_admin:
        user = await user_service.get_user_by_username(username)
        return UserResponse.model_validate(user)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied, should be admin / Нет доступа, только для админа"
        )


@router.get(
    "/",
    response_model=UserList,
    summary="List users / Список пользователей",
    description="Get paginated list of users / Получить список пользователей с пагинацией"
)
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip / Количество записей пропустить"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return / Максимум записей вернуть"),
    active_only: bool = Query(False, description="Return only active users / Только активные пользователи"),
    current_user: User = Depends(get_current_user)
) -> UserList:
    if current_user.is_admin:
        users, total = await user_service.list_users(skip, limit, active_only)
        user_responses = [UserResponse.model_validate(user) for user in users]
        return UserList(total=total, users=user_responses)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied, should be admin / Нет доступа, только для админа"
        )


@router.get(
    "/search/",
    response_model=list[UserResponse],
    summary="Search users / Поиск пользователей",
    description="Search users by username, email or full name / Поиск по имени, email или полному имени"
)
async def search_users(
    q: str = Query(..., min_length=1, description="Search query / Поисковый запрос"),
    skip: int = Query(0, ge=0, description="Number of records to skip / Количество записей пропустить"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return / Максимум записей вернуть"),
    current_user: User = Depends(get_current_user)
) -> list[UserResponse]:
    if current_user.is_admin:
        users = await user_service.search_users(q, skip, limit)  # pragma: no cover
        return [UserResponse.model_validate(user) for user in users]  # pragma: no cover
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied, should be admin / Нет доступа, только для админа"
        )

@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user / Обновить пользователя",
    description="Update user information / Обновить информацию о пользователе"
)
async def update_user(user_data: UserUpdate, current_user: User = Depends(get_current_user)) -> UserResponse:
    user = await user_service.update_user(current_user.id, user_data)
    return UserResponse.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user / Удалить пользователя",
    description="Delete user by ID / Удалить пользователя по ID"
)
async def delete_user(current_user: User = Depends(get_current_user)) -> None:
    await user_service.delete_user(current_user.id)
    # Return 204 No Content / Вернуть 204 No Content