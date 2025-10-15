from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.models.journal import JournalLine, JournalEntry
from app.models.account import Account, AccountType
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/trial-balance/{org_id}")
def trial_balance(org_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Sum debits and credits per account
    results = (
        db.query(
            Account.id.label("account_id"),
            Account.code,
            Account.name,
            Account.type,
            func.sum(JournalLine.debit).label("debit_sum"),
            func.sum(JournalLine.credit).label("credit_sum"),
        )
        .join(JournalLine, JournalLine.account_id == Account.id)
        .join(JournalEntry, JournalEntry.id == JournalLine.entry_id)
        .filter(Account.organization_id == org_id)
        .group_by(Account.id, Account.code, Account.name, Account.type)
        .order_by(Account.code)
        .all()
    )

    data = []
    total_debits = 0
    total_credits = 0
    for row in results:
        debit = float(row.debit_sum or 0)
        credit = float(row.credit_sum or 0)
        balance = debit - credit
        normal = 1 if row.type in (AccountType.ASSET, AccountType.EXPENSE) else -1
        tb_debit = balance if balance * normal > 0 else 0
        tb_credit = -balance if balance * normal < 0 else 0
        data.append({
            "account_id": row.account_id,
            "code": row.code,
            "name": row.name,
            "type": row.type.value,
            "debit": round(tb_debit, 2),
            "credit": round(tb_credit, 2),
        })
        total_debits += tb_debit
        total_credits += tb_credit

    return {
        "rows": data,
        "totals": {"debit": round(total_debits, 2), "credit": round(total_credits, 2)},
    }
