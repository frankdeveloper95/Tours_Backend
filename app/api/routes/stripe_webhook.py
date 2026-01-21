import datetime
import stripe
from fastapi import APIRouter, Request, Header, HTTPException
from sqlmodel import select

from app.auth.deps import SessionDep
from app.core.config import settings
from app.models import Reservas, Estado_Reserva, ReservaEnum

router = APIRouter(tags=["Stripe Webhook"])
stripe.api_key = str(settings.STRIPE_SECRET_KEY)


@router.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    session: SessionDep,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=stripe_signature,
            secret=str(settings.STRIPE_WEBHOOK_SECRET),
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Webhook inválido")

    event_type = event["type"]

    # ============================================================
    # 1) FLUJO NUEVO: Checkout Session completado
    # ============================================================
    if event_type == "checkout.session.completed":
        session_obj = event["data"]["object"]

        # Stripe Checkout → metadata["reserva_id"]
        reserva_id = session_obj.get("metadata", {}).get("reserva_id")

        if not reserva_id:
            return {"ok": True}

        reserva = session.get(Reservas, int(reserva_id))

        if not reserva:
            return {"ok": True}

        # Obtener estado PAGADA
        estado_pagada = session.exec(
            select(Estado_Reserva).where(Estado_Reserva.estado == ReservaEnum.PAGADA)
        ).first()

        reserva.id_reserva_estado = estado_pagada.id
        reserva.updated_date = datetime.datetime.now()
        reserva.checkout_session_id = session_obj["id"]

        session.add(reserva)
        session.commit()

        return {"ok": True}

    # ============================================================
    # 2) FLUJO VIEJO: PaymentIntent (Stripe Elements)
    # ============================================================
    if event_type == "payment_intent.succeeded":
        pi = event["data"]["object"]

        reserva_id = pi.metadata.get("reserva_id")

        reserva = None

        if reserva_id:
            reserva = session.get(Reservas, int(reserva_id))
        else:
            reserva = session.exec(
                select(Reservas).where(Reservas.payment_intent_id == pi.id)
            ).first()

        if not reserva:
            return {"ok": True}

        estado_pagada = session.exec(
            select(Estado_Reserva).where(Estado_Reserva.estado == ReservaEnum.PAGADA)
        ).first()

        reserva.id_reserva_estado = estado_pagada.id
        reserva.updated_date = datetime.datetime.now()

        session.add(reserva)
        session.commit()

        return {"ok": True}

    return {"ok": True}
