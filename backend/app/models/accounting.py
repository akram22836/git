from __future__ import annotations

import enum
from datetime import date, datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class AccountType(str, enum.Enum):
    asset = "asset"
    liability = "liability"
    equity = "equity"
    revenue = "revenue"
    expense = "expense"


class Account(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(index=True, nullable=False)
    name: str = Field(nullable=False)
    type: AccountType = Field(nullable=False)
    parent_id: Optional[int] = Field(default=None, foreign_key="account.id")
    is_active: bool = Field(default=True, nullable=False)


class JournalEntry(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: date = Field(nullable=False)
    reference: Optional[str] = None
    description: Optional[str] = None
    posted: bool = Field(default=False, nullable=False)
    posted_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class JournalLine(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    journal_entry_id: int = Field(foreign_key="journalentry.id", nullable=False)
    account_id: int = Field(foreign_key="account.id", nullable=False)
    debit: float = Field(default=0.0, nullable=False)
    credit: float = Field(default=0.0, nullable=False)
