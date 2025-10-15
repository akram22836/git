from __future__ import annotations

from typing import Annotated, Generator

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt

from app.core.config import settings
from app.schemas.auth import TokenPayload


def get_token_authorization_header(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        scheme, token = authorization.split(" ", 1)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme")
    return token


def get_current_user_id(authorization: Annotated[str | None, Depends()] = None) -> int:
    token = get_token_authorization_header(authorization)
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        token_data = TokenPayload(**payload)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials")
    return int(token_data.sub)
