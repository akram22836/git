from __future__ import annotations

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.accounting import Account, JournalEntry, JournalLine
from app.schemas.accounting import (
    AccountCreate,
    AccountRead,
    JournalEntryCreate,
    JournalEntryRead,
    TrialBalanceLine,
)
from app.services.posting import post_entry

router = APIRouter()


@router.post("/accounts", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
def create_account(payload: AccountCreate, session: Session = Depends(get_session)) -> AccountRead:
    existing = session.exec(select(Account).where(Account.code == payload.code)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Account code already exists")
    account = Account(code=payload.code, name=payload.name, type=payload.type, parent_id=payload.parent_id)
    session.add(account)
    session.commit()
    session.refresh(account)
    return AccountRead(id=account.id, code=account.code, name=account.name, type=account.type, parent_id=account.parent_id)


@router.post("/journals", response_model=JournalEntryRead, status_code=status.HTTP_201_CREATED)
def create_journal(payload: JournalEntryCreate, session: Session = Depends(get_session)) -> JournalEntryRead:
    entry = JournalEntry(date=payload.date, reference=payload.reference, description=payload.description)
    session.add(entry)
    session.commit()
    session.refresh(entry)

    for line in payload.lines:
        jl = JournalLine(
            journal_entry_id=entry.id,
            account_id=line.account_id,
            debit=line.debit,
            credit=line.credit,
        )
        session.add(jl)
    session.commit()

    return JournalEntryRead(id=entry.id, date=entry.date, posted=entry.posted, reference=entry.reference, description=entry.description)


@router.post("/journals/{entry_id}/post", response_model=JournalEntryRead)
def post_journal(entry_id: int, session: Session = Depends(get_session)) -> JournalEntryRead:
    entry = session.get(JournalEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    entry = post_entry(session, entry)
    return JournalEntryRead(id=entry.id, date=entry.date, posted=entry.posted, reference=entry.reference, description=entry.description)


@router.get("/reports/trial-balance", response_model=List[TrialBalanceLine])
def trial_balance(date_from: date | None = None, date_to: date | None = None, session: Session = Depends(get_session)) -> list[TrialBalanceLine]:
    # Simplified trial balance ignoring periods for brevity
    # In production, filter by date range using JournalEntry.date
    accounts = session.exec(select(Account)).all()
    results: list[TrialBalanceLine] = []
    for acc in accounts:
        debit_total = session.exec(
            select(JournalLine).where(JournalLine.account_id == acc.id)
        ).all()
        debit_sum = sum(l.debit for l in debit_total)
        credit_sum = sum(l.credit for l in debit_total)
        results.append(
            TrialBalanceLine(
                account_id=acc.id,
                code=acc.code,
                name=acc.name,
                debit_total=debit_sum,
                credit_total=credit_sum,
                balance=round(debit_sum - credit_sum, 2),
            )
        )
    return results
