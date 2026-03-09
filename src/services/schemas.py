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
    is_active: bool = Field(
        default=True,
        description="Whether user is active / Активен ли пользователь"
    )


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

class UserInDB(BaseModel):
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

class LinkCreate(BaseModel):
    original_url: str = Field(
        ...,
        max_length=255,
        description="Original URL / Оригинальная URL-адреса"
    )
    short_code: str = Field(
        default=None,
        max_length=255,
        description="Short code / Короткий код"
    )
    project: str = Field(
        default=None,
        max_length=255,
        description="Project / Проект"
    )
    
class LinkUpdate(BaseModel):
    original_url: Optional[str] = Field(None, max_length=255)
    short_code: Optional[str] = Field(None, max_length=255)
    user_registred: Optional[bool] = None
    project: Optional[str] = Field(None, max_length=255)

class LinkInDB(BaseModel):
    id: int
    original_url: str
    short_code: str
    user_registred: bool
    project: Optional[str] = None
    transitions: int
    last_transition_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(  
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "original_url": "https://example.com",
                "short_code": "1234567890",
                "user_registred": True,
                "project": "project",
                "transitions": 100,
                "last_transition_at": "2024-01-01T12:00:00",
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00"
            }
        }
    )


class LinkResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    user_registred: bool
    project: Optional[str] = None
    transitions: int
    last_transition_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "original_url": "https://example.com",
                "short_code": "1234567890",
                "user_registred": True,
                "project": "project",
                "transitions": 100,
                "last_transition_at": "2024-01-01T12:00:00",
            }
        }
    )


class LinkList(BaseModel):
    """
    DTO for paginated list of links / DTO для списка ссылок

    """
    total: int = Field(description="Total number of links / Общее количество ссылок")
    links: list[LinkResponse] = Field(description="List of links / Список ссылок")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 2, 
                "links": [
                    {
                        "id": 1,
                        "original_url": "https://example.com",
                        "short_code": "1234567890",
                        "user_registred": True,
                        "project": "project",
                        "transitions": 100,
                        "last_transition_at": "2024-01-01T12:00:00",
                    }
                ]
            }
        }
    )
