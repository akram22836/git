from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationOut
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/", response_model=OrganizationOut)
def create_org(payload: OrganizationCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    existing = db.query(Organization).filter(Organization.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Organization name already exists")
    org = Organization(name=payload.name)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.get("/", response_model=list[OrganizationOut])
def list_orgs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Organization).all()
