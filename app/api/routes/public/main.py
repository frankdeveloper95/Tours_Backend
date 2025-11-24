from fastapi import APIRouter
from app.api.routes.public import tours, reservas
api_router_public = APIRouter()

api_router_public.include_router(tours.router)
api_router_public.include_router(reservas.router)