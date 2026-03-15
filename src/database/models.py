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
    links: Mapped[list["Link"]] = relationship(back_populates="user", cascade="all, delete-orphan", lazy="selectin", single_parent=True, foreign_keys="[Link.user_id]")
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
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def activate(self) -> None:
        """Activate user / Активировать пользователя"""
        self.is_active = True

    def deactivate(self) -> None:
        """Deactivate user / Деактивировать пользователя"""
        self.is_active = False
    

class Link(Base):

    __tablename__ = "links"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    original_url: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    short_code: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    transitions: Mapped[int] = mapped_column(Integer, default=0)
    last_transition_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    project: Mapped[str] = mapped_column(String(255), index=True, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("short-link.users.id", ondelete="SET NULL"), nullable=True, index=True)
    user: Mapped[Optional["User"]] = relationship(back_populates="links", lazy="selectin", foreign_keys=[user_id])
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
        return f"<Link(id={self.id}, short_code='{self.short_code}', original_url='{self.original_url}')>"
