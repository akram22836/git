from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Timestamped(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class UserBase(SQLModel):
    email: str = Field(index=True, nullable=False, unique=True)
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class User(UserBase, Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
