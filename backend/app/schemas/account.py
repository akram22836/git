from __future__ import annotations

from pydantic import BaseModel
from app.models.account import AccountType


class AccountCreate(BaseModel):
    code: str
    name: str
    type: AccountType
    organization_id: int


class AccountOut(BaseModel):
    id: int
    code: str
    name: str
    type: AccountType

    class Config:
        from_attributes = True
