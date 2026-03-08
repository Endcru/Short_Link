from database.database import Base
from sqlalchemy import String, DateTime, Boolean, func, JSON, Integer, ForeignKey, Enum, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, List

class User(Base):

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    def __repr__(self) -> str:
        return f"<User(id={self.id}, user_id='{self.user_id}')>"
    
    def activate(self) -> None:
        """Activate user / Активировать пользователя"""
        self.is_active = True

    def deactivate(self) -> None:
        """Deactivate user / Деактивировать пользователя"""
        self.is_active = False
    
    def profile_filed(self) -> Boolean:
        if self.age is None or self.city is None or self.height is None or self.weight is None or self.activity is None:
            return False
        return True