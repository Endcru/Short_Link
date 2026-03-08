from datetime import datetime
from typing import Optional, Annotated, Union, Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Unique username / Уникальное имя пользователя"
    )
    email: EmailStr = Field(
        ...,
        description="User email address / Email адрес пользователя"
    )
    password: str = Field(
        ...,
        max_length=255,
        description="User password / password пользователя"
    )
    api_key: str = Field(
        ...,
        max_length=255,
        description="DEEPSEEK API KEY"
    )
    is_active: bool = Field(
        default=True,
        description="Whether user is active / Активен ли пользователь"
    )


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    api_key: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

class UserInDB(BaseModel):
    id: int
    username: str
    email: str
    api_key: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "johndoe",
                "email": "john@example.com",
                "api-key": "api-key",
                "is_active": True,
                "is_admin": True,
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00"
            }
        }
    )


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "johndoe",
                "email": "john@example.com",
                "is_active": True,
                "is_admin": True,
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00"
            }
        }
    )


class UserList(BaseModel):
    """
    DTO for paginated list of users / DTO для списка пользователей

    """
    total: int = Field(description="Total number of users / Общее количество пользователей")
    users: list[UserResponse] = Field(description="List of users / Список пользователей")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 2,
                "users": [
                    {
                        "id": 1,
                        "username": "johndoe",
                        "email": "john@example.com",
                        "is_active": True,
                        "is_admin": False,
                        "created_at": "2024-01-01T12:00:00",
                        "updated_at": "2024-01-01T12:00:00"
                    }
                ]
            }
        }
    )
