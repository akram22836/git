from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.accounting import AccountType


class AccountCreate(BaseModel):
    code: str
    name: str
    type: AccountType
    parent_id: Optional[int] = None


class AccountRead(BaseModel):
    id: int
    code: str
    name: str
    type: AccountType
    parent_id: Optional[int] = None


class JournalLineCreate(BaseModel):
    account_id: int
    debit: float = 0.0
    credit: float = 0.0

    @field_validator("debit", "credit")
    @classmethod
    def non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Amounts must be non-negative")
        return v


class JournalEntryCreate(BaseModel):
    date: date
    reference: Optional[str] = None
    description: Optional[str] = None
    lines: List[JournalLineCreate] = Field(min_length=2)


class JournalEntryRead(BaseModel):
    id: int
    date: date
    posted: bool
    reference: Optional[str] = None
    description: Optional[str] = None


class TrialBalanceLine(BaseModel):
    account_id: int
    code: str
    name: str
    debit_total: float
    credit_total: float
    balance: float
