from fastapi import APIRouter
from . import auth

api = APIRouter()
api.include_router(auth.r, prefix="/auth")
