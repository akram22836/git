from __future__ import annotations

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    organization_id: int | None = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    is_active: bool
    organization_id: int | None

    class Config:
        from_attributes = True
