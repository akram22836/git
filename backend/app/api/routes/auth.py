from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.services.security import verify_password, get_password_hash, create_access_token
from app.core.config import Token

router = APIRouter()


@router.post("/login", response_model=Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    access_token = create_access_token(subject=str(user.id), org_id=user.organization_id)
    return Token(access_token=access_token)


@router.post("/register", response_model=Token)
def register(email: str, password: str, full_name: str | None = None, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(email=email, hashed_password=get_password_hash(password), full_name=full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token = create_access_token(subject=str(user.id), org_id=user.organization_id)
    return Token(access_token=access_token)
