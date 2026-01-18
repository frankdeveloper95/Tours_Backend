from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import stripe
import uuid

from app.auth.deps import get_current_active_user, SessionDep
from app.core.config import settings
from app.models import Stripe, Tour, User
 

router = APIRouter(tags=["Checkout"])
stripe.api_key = str(settings.STRIPE_SECRET_KEY)
DOMAIN = 'http://localhost:5173/'


@router.post('/checkout')
async def checkout(
    product: Stripe,
    session: SessionDep,
    current_user: User = Depends(get_current_active_user)
):
    tour = session.get(Tour, product.product_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour no encontrado")

    unit_amount = int(round(float(tour.precio) * 100))

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[{
                "price_data": {
                    "product_data": {"name": tour.nombre},
                    "unit_amount": unit_amount,
                    "currency": "usd"
                },
                "quantity": 1
            }],

            # ✅ guarda quién pagó (usuario)
            client_reference_id=str(current_user.id),

            # ✅ guarda qué se pagó (tour)
            metadata={
                "id_tour": str(tour.id),
                "numero_personas": str(getattr(product, "numero_personas", 1)),
            },

            cancel_url=DOMAIN + "home",
            success_url=DOMAIN + "checkout?success=true",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={"url": checkout_session.url})