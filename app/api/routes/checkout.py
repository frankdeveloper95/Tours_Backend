from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import stripe
from app.api.deps import get_current_active_user
from app.core.config import settings
from app.models import Stripe, Tour
from app.api.deps import SessionDep

router = APIRouter(tags=["Checkout"], dependencies=[Depends(get_current_active_user)])
stripe.api_key = str(settings.STRIPE_SECRET_KEY)
DOMAIN = 'http://localhost:5173/'


@router.post('/checkout')
async def checkout(product_id: Stripe, session: SessionDep):
    tour = session.get(Tour, product_id.product_id)
    unit_amount = int(round(float(tour.precio) * 100))
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            cancel_url = DOMAIN + 'home',
            line_items=[{
                "price_data": {
                    "product_data": {
                        "name": tour.nombre,
                    },
                    "unit_amount": unit_amount,
                    'currency': 'usd'
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=DOMAIN + 'checkout?success=true'
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(content={'url': checkout_session.url})
