from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.models.journal import JournalEntry, JournalLine
from app.models.account import Account
from app.schemas.journal import JournalEntryCreate, JournalEntryOut, JournalLineOut
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/", response_model=JournalEntryOut)
def create_journal_entry(payload: JournalEntryCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    total_debit = sum([line.debit for line in payload.lines])
    total_credit = sum([line.credit for line in payload.lines])
    if total_debit != total_credit:
        raise HTTPException(status_code=400, detail="Debits and credits must balance")

    # validate accounts exist in org
    account_ids = [l.account_id for l in payload.lines]
    accounts = db.query(Account.id).filter(Account.id.in_(account_ids), Account.organization_id == payload.organization_id).all()
    if len(accounts) != len(account_ids):
        raise HTTPException(status_code=400, detail="Invalid account(s) for organization")

    entry = JournalEntry(
        organization_id=payload.organization_id,
        reference=payload.reference,
        description=payload.description,
        entry_date=payload.entry_date,
    )
    db.add(entry)
    db.flush()

    lines = [
        JournalLine(entry_id=entry.id, account_id=l.account_id, description=l.description, debit=l.debit, credit=l.credit)
        for l in payload.lines
    ]
    db.add_all(lines)
    db.commit()
    db.refresh(entry)

    entry_lines = db.query(JournalLine).filter(JournalLine.entry_id == entry.id).all()
    return JournalEntryOut(
        id=entry.id,
        organization_id=entry.organization_id,
        entry_date=entry.entry_date,
        reference=entry.reference,
        description=entry.description,
        lines=[JournalLineOut.model_validate(l) for l in entry_lines],
    )
