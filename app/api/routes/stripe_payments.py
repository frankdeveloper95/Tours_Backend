from fastapi import APIRouter, HTTPException, Depends
from app.auth.deps import SessionDep, get_current_active_user
from app.reservas.service import ReservasService
from app.pagos.service import StripeService
from app.models import ReservasCreatePublic, User
import stripe
import os

router = APIRouter(prefix="/pagos", tags=["Pagos"])

STRIPE_SECRET_KEY = os.getenv("YOUR_SECRET_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

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
    monto = reserva.numero_personas * 10000
    pi = StripeService.create_payment_intent(monto, reserva.id)

    reserva.payment_intent_id = pi.id
    session.add(reserva)
    session.commit()

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
        # 1) Crear reserva
        reserva = ReservasService.create_reserva(session, reserva_in, current_user)

        # 2) Calcular monto
        monto = reserva.numero_personas * 10000  # en centavos

        # 3) Crear sesión de Stripe Checkout
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Reserva Tour #{reserva.id}",
                            "description": f"Fecha: {reserva.fecha_reserva}",
                        },
                        "unit_amount": monto,
                    },
                    "quantity": 1,
                }
            ],
            customer_email=current_user.email, 
            metadata={"reserva_id": str(reserva.id)}, 
            success_url=f"{FRONTEND_URL}/protected/reservas", 
            cancel_url=f"{FRONTEND_URL}/protected/checkout?tourId={reserva.id_tour}", )

        # 4) Guardar checkout_session_id
        reserva.checkout_session_id = checkout_session.id
        session.add(reserva)
        session.commit()

        # 5) Devolver URL de Stripe
        return {"url": checkout_session.url}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
