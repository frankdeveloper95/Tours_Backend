import datetime
import uuid
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

    if event["type"] == "checkout.session.completed":
        s = event["data"]["object"]

        user_id_str = s.get("client_reference_id")
        md = s.get("metadata") or {}
        id_tour = md.get("id_tour")
        numero_personas = int(md.get("numero_personas") or 1)

        if not user_id_str or not id_tour:
            return {"ok": True}

        user_id = uuid.UUID(user_id_str)
        now = datetime.datetime.now()

        # ✅ estado PAGADA (por tu tabla estado_reserva)
        pagada = session.exec(
            select(Estado_Reserva).where(Estado_Reserva.estado == ReservaEnum.PAGADA)
        ).first()

        id_estado_pagada = pagada.id if pagada else 1

        # ✅ crea reserva
        reserva = Reservas(
            id_tour=int(id_tour),
            id_usuario=user_id,
            id_reserva_estado=id_estado_pagada,
            nombre_cliente=(s.get("customer_details") or {}).get("name") or "Cliente",
            email_cliente=(s.get("customer_details") or {}).get("email") or "sin-email",
            numero_personas=numero_personas,
            fecha_reserva=now,
            created_date=now,
            id_usuario_created=user_id,
        )

        session.add(reserva)
        session.commit()

    return {"ok": True}
