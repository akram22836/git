from fastapi import APIRouter

from app.api.v1 import users as users_api
from app.api.v1 import auth as auth_api
from app.api.v1 import accounting as accounting_api

api_router = APIRouter()
api_router.include_router(auth_api.router, prefix="/auth", tags=["auth"])
api_router.include_router(users_api.router, prefix="/users", tags=["users"])
api_router.include_router(accounting_api.router, tags=["accounting"])