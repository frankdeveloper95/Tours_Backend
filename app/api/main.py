from fastapi import APIRouter
from app.api.routes import (
    login, reservas_admin, users, operadora, guia,
    tours_public, tours_admin,
    zarpe, checkout,
    stripe_payments,      # ← NUEVO
    stripe_webhook,
    reservas_public
)

api_router = APIRouter()

# Rutas públicas / auth
api_router.include_router(login.router)
api_router.include_router(users.router)

# Rutas de negocio
api_router.include_router(operadora.router)
api_router.include_router(guia.router)
api_router.include_router(tours_public.router)
api_router.include_router(tours_admin.router)
api_router.include_router(reservas_public.router)
api_router.include_router(reservas_admin.router)
api_router.include_router(zarpe.router)
api_router.include_router(checkout.router)

# Stripe
api_router.include_router(stripe_payments.router)   # ← NECESARIO
api_router.include_router(stripe_webhook.router)
