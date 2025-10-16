from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

from app.api.deps import get_current_user_id
from app.db.session import get_session
from app.models.base import User

router = APIRouter()
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str | None = None
    password: str


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, session: Session = Depends(get_session)) -> UserRead:
    existing = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=password_context.hash(user_in.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserRead(id=user.id, email=user.email, full_name=user.full_name)


@router.get("/", response_model=List[UserRead])
def list_users(session: Session = Depends(get_session), current_user_id: int = Depends(get_current_user_id)) -> list[UserRead]:
    users = session.exec(select(User)).all()
    return [UserRead(id=u.id, email=u.email, full_name=u.full_name) for u in users]
