from fastapi import APIRouter
from app.api.routes.public import auth_register
api_router_public = APIRouter()


api_router_public.include_router(auth_register.router)