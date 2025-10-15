from __future__ import annotations

from datetime import datetime
from typing import Iterable

from fastapi import HTTPException
from sqlmodel import Session

from app.models.accounting import JournalEntry, JournalLine


def validate_balanced(lines: Iterable[JournalLine]) -> None:
    debit_total = sum(l.debit for l in lines)
    credit_total = sum(l.credit for l in lines)
    if round(debit_total - credit_total, 2) != 0:
        raise HTTPException(status_code=400, detail="Journal entry not balanced (debits != credits)")
    for l in lines:
        if (l.debit > 0 and l.credit > 0) or (l.debit == 0 and l.credit == 0):
            raise HTTPException(status_code=400, detail="Each line must be either debit or credit, not both or none")


def post_entry(session: Session, entry: JournalEntry) -> JournalEntry:
    if entry.posted:
        raise HTTPException(status_code=400, detail="Entry already posted")

    lines = session.exec(
        session.query(JournalLine).filter(JournalLine.journal_entry_id == entry.id)
    ).all()
    validate_balanced(lines)

    entry.posted = True
    entry.posted_at = datetime.utcnow()
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry
