from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.account import Account, AccountType
from app.schemas.account import AccountCreate, AccountOut
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/", response_model=AccountOut)
def create_account(payload: AccountCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    existing = (
        db.query(Account)
        .filter(Account.organization_id == payload.organization_id, Account.code == payload.code)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Account code exists in organization")
    account = Account(
        code=payload.code,
        name=payload.name,
        type=payload.type,
        organization_id=payload.organization_id,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get("/org/{org_id}", response_model=list[AccountOut])
def list_accounts(org_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Account).filter(Account.organization_id == org_id).all()
