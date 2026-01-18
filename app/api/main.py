from fastapi import APIRouter
from app.api.routes import (
    login, reservas_public, reservas_admin, users, operadora, guia,
    tours_public, tours_admin,
    zarpe, checkout, stripe_webhook
)

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(operadora.router)
api_router.include_router(guia.router)
api_router.include_router(tours_public.router)
api_router.include_router(tours_admin.router)
api_router.include_router(reservas_public.router)
api_router.include_router(zarpe.router)
api_router.include_router(checkout.router)
api_router.include_router(stripe_webhook.router)
api_router.include_router(reservas_admin.router)
