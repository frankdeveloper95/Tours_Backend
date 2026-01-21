import json

import stripe
from fastapi import APIRouter, HTTPException, Depends

from app.auth.deps import SessionDep, get_current_active_user
from app.core.config import settings
from app.models import ReservasCreatePublic, User, Tour
from app.pagos.service import StripeService
from app.reservas.service import ReservasService

router = APIRouter(prefix="/pagos", tags=["Pagos"])

STRIPE_SECRET_KEY = str(settings.STRIPE_SECRET_KEY)
FRONTEND_URL = str(settings.FRONTEND_HOST) + "/"

stripe.api_key = STRIPE_SECRET_KEY


# ============================================================
# 1) TU ENDPOINT ACTUAL (PaymentIntent) — LO DEJO INTACTO
# ============================================================
@router.post("/create-payment-intent")
def create_payment_intent(
    reserva_in: ReservasCreatePublic,
    session: SessionDep,
    current_user: User = Depends(get_current_active_user),
):
    reserva = ReservasService.create_reserva(session, reserva_in, current_user)
    unit_amount = int(round(float(reserva.tour.precio) * 100))
    monto = reserva.numero_personas * unit_amount
    pi = StripeService.create_payment_intent(monto, reserva.id)

    reserva.payment_intent_id = pi.id

    return {
        "clientSecret": pi.client_secret,
        "paymentIntentId": pi.id,
        "reservaId": reserva.id,
    }


# ============================================================
# 2) NUEVO ENDPOINT: STRIPE CHECKOUT (redirige a pasarela)
# ============================================================
@router.post("/create-checkout-session")
def create_checkout_session(
    reserva_in: ReservasCreatePublic,
    session: SessionDep,
    current_user: User = Depends(get_current_active_user),
):
    try:
        # fetch the Tour (do not treat Tour as a Reserva)
        tour = session.get(Tour, reserva_in.id_tour)
        if not tour:
            raise HTTPException(status_code=404, detail="Tour not found")

        # calculate amount (price * number_of_people) in cents
        unit_amount = int(round(float(tour.precio) * 100))
        monto = reserva_in.numero_personas * unit_amount  # in cents

        # compact metadata payload (strings only)
        reserva_payload = {
            "tour_id": str(reserva_in.id_tour),
            "fecha_reserva": reserva_in.fecha_reserva.isoformat(),
            "numero_personas": str(reserva_in.numero_personas),
            "user_email": current_user.email,
        }

        # create Stripe Checkout session (do not persist Reserva here)
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Reserva Tour {tour.nombre}",
                            "description": f"Fecha: {reserva_in.fecha_reserva}",
                        },
                        "unit_amount": monto,
                    },
                    "quantity": 1,
                }
            ],
            customer_email=current_user.email,
            metadata={"reserva_payload": json.dumps(reserva_payload)},
            success_url=f"{FRONTEND_URL}protected/reservas",
            cancel_url=f"{FRONTEND_URL}home",
        )

        return {"url": checkout_session.url}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))