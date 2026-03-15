from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


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
    custom_alias: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Short code / Короткий код"
    )
    project: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Project / Проект"
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Expiration datetime (minute precision) / Время истечения срока (точность до минуты)."
    )

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value:
            now = datetime.now(timezone.utc)
            val = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
            if val <= now:
                raise ValueError("expires_at must be in the future")
        return value

class LinkUpdate(BaseModel):
    custom_alias: Optional[str] = Field(None, max_length=255)
    project: Optional[str] = Field(None, max_length=255)
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Expiration datetime (minute precision) / Время истечения срока (точность до минуты)."
    )

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value:
            now = datetime.now(timezone.utc)
            val = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
            if val <= now:
                raise ValueError("expires_at must be in the future")
        return value

class LinkInDB(BaseModel):
    id: int
    original_url: str
    short_code: str
    user_id: Optional[int] = None
    project: Optional[str] = None
    transitions: int
    last_transition_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    user_id: Optional[int]

    model_config = ConfigDict(  
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "original_url": "https://example.com",
                "short_code": "1234567890",
                "user_id": 1,
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
    user_id: Optional[int] = None
    project: Optional[str] = None
    transitions: int
    last_transition_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "original_url": "https://example.com",
                "short_code": "1234567890",
                "user_id": 1,
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
