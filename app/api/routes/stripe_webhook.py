import datetime
import json
import logging
import stripe
from fastapi import APIRouter, Request, Header, HTTPException
from sqlmodel import select

from app.auth.deps import SessionDep
from app.core.config import settings
from app.models import Reservas, Estado_Reserva, ReservaEnum
from app.reservas.service import ReservasService

router = APIRouter(tags=["Stripe Webhook"])
stripe.api_key = str(settings.STRIPE_SECRET_KEY)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@router.post("/stripe/webhook/")
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

    logger.info("Stripe event received: %s", event_type)
    logger.debug("Full event data: %s", event.get("data", {}).get("object"))

    if event_type == "checkout.session.completed":
        session_obj = event["data"]["object"]

        # metadata may store a JSON string under 'reserva_payload'
        reserva_payload_raw = session_obj.get("metadata", {}) or {}
        reserva_payload_raw = reserva_payload_raw.get("reserva_payload") or reserva_payload_raw.get("payload") or None

        if not reserva_payload_raw:
            # metadata missing - log and skip to avoid DB integrity errors
            logger.error("checkout.session.completed missing reserva_payload metadata; session id: %s", session_obj.get("id"))
            return {"ok": True}

        try:
            reserva_payload = json.loads(reserva_payload_raw) if isinstance(reserva_payload_raw, str) else reserva_payload_raw
        except Exception:
            logger.exception("Invalid JSON in reserva_payload")
            return {"ok": True}

        # validate minimal required fields before attempting DB insert
        if not (reserva_payload.get("tour_id") or reserva_payload.get("id_tour")):
            logger.error("reserva_payload missing tour_id: %s", reserva_payload)
            return {"ok": True}

        try:
            reserva = ReservasService.create_reserva_from_metadata(session, reserva_payload, stripe_session_obj=session_obj)
        except ValueError as ve:
            logger.error("Skipping reserva creation: %s", ve)
            return {"ok": True}
        except Exception:
            logger.exception("Error creating reserva from metadata")
            return {"ok": True}

        estado_pagada = session.exec(
            select(Estado_Reserva).where(Estado_Reserva.estado == ReservaEnum.PAGADA)
        ).first()

        reserva.id_reserva_estado = estado_pagada.id if estado_pagada else reserva.id_reserva_estado
        reserva.updated_date = datetime.datetime.now()
        reserva.checkout_session_id = session_obj.get("id")

        session.add(reserva)
        session.commit()
        session.refresh(reserva)

        logger.info("Reserva created/updated from checkout.session.completed id=%s tour=%s", getattr(reserva, "id", None), getattr(reserva, "id_tour", None))
        return {"ok": True}

    # existing payment_intent.succeeded handler unchanged but add safe checks
    if event_type == "payment_intent.succeeded":
        pi = event["data"]["object"]

        reserva_id = getattr(pi, "metadata", {}) and pi.metadata.get("reserva_id")
        reserva = None

        if reserva_id:
            try:
                reserva = session.get(Reservas, int(reserva_id))
            except Exception:
                reserva = None

        if not reserva:
            reserva = session.exec(
                select(Reservas).where(Reservas.payment_intent_id == pi.get("id"))
            ).first()

        if not reserva:
            logger.info("No reserva linked to payment_intent %s", pi.get("id"))
            return {"ok": True}

        estado_pagada = session.exec(
            select(Estado_Reserva).where(Estado_Reserva.estado == ReservaEnum.PAGADA)
        ).first()

        reserva.id_reserva_estado = estado_pagada.id if estado_pagada else reserva.id_reserva_estado
        reserva.updated_date = datetime.datetime.now()

        session.add(reserva)
        session.commit()
        session.refresh(reserva)

        return {"ok": True}

    return {"ok": True}