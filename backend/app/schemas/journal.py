from __future__ import annotations

from pydantic import BaseModel
from datetime import date
from decimal import Decimal


class JournalLineIn(BaseModel):
    account_id: int
    description: str | None = None
    debit: Decimal = Decimal("0")
    credit: Decimal = Decimal("0")


class JournalEntryCreate(BaseModel):
    organization_id: int
    entry_date: date
    reference: str | None = None
    description: str | None = None
    lines: list[JournalLineIn]


class JournalLineOut(BaseModel):
    id: int
    account_id: int
    description: str | None
    debit: Decimal
    credit: Decimal

    class Config:
        from_attributes = True


class JournalEntryOut(BaseModel):
    id: int
    organization_id: int
    entry_date: date
    reference: str | None
    description: str | None
    lines: list[JournalLineOut]

    class Config:
        from_attributes = True
