from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.base import User
from app.schemas.auth import Token, create_access_token

router = APIRouter()
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginInput(BaseModel):
    email: str
    password: str


@router.post("/login", response_model=Token)
def login(data: LoginInput, session: Session = Depends(get_session)) -> Token:
    user = session.exec(select(User).where(User.email == data.email)).first()
    if not user or not password_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token = create_access_token(subject=str(user.id), expires_delta=timedelta(minutes=60))
    return Token(access_token=access_token)
