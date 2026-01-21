import datetime as dt
from typing import Optional

from sqlmodel import select
from fastapi import HTTPException

from app.auth.deps import SessionDep
from app.models import (
    Reservas,
    ReservasCreatePublic,
    ReservasCreateAdmin,
    ReservasUpdate,
    User
)
from app.reservas.repository import ReservasRepository

# Estados de reserva
ESTADO_RESERVA_PENDIENTE = 2
ESTADO_RESERVA_CANCELADA = 3
ESTADO_RESERVA_PAGADA = 1   # ← FALTABA ESTA CONSTANTE


class ReservasService:

    # ============================================================
    # Crear reserva pública
    # ============================================================
    @staticmethod
    def create_reserva(
        session: SessionDep,
        reserva_in: ReservasCreatePublic,
        current_user: User,
    ) -> Reservas:
        tour = ReservasRepository.get_tour(session, reserva_in.id_tour)

        cantidad = reserva_in.numero_personas
        if cantidad <= 0:
            raise HTTPException(status_code=400, detail="Número de personas inválido")

        if tour.capacidad_maxima is not None and cantidad > tour.capacidad_maxima:
            raise HTTPException(
                status_code=400,
                detail="La cantidad supera la capacidad máxima del tour",
            )

        if hasattr(tour, "activo") and not tour.activo:
            raise HTTPException(status_code=400, detail="El tour no está disponible")

        if reserva_in.fecha_reserva.date() < dt.date.today():
            raise HTTPException(status_code=400, detail="La fecha de reserva no puede ser en el pasado")

        reserva = Reservas(
            id_tour=reserva_in.id_tour,
            id_usuario=current_user.id,
            id_reserva_estado=ESTADO_RESERVA_PENDIENTE,
            nombre_cliente=(
                reserva_in.nombre_cliente
                or f"{(current_user.nombre or '').strip()} {(current_user.apellido or '').strip()}".strip()
            ),
            email_cliente=reserva_in.email_cliente or current_user.email,
            numero_personas=reserva_in.numero_personas,
            fecha_reserva=reserva_in.fecha_reserva,
            created_date=dt.datetime.now(),
            id_usuario_created=current_user.id,
        )

        return ReservasRepository.create(session, reserva)

    # ============================================================
    # Crear reserva desde admin
    # ============================================================
    @staticmethod
    def create_reserva_admin(
        session: SessionDep,
        reserva_in: ReservasCreateAdmin,
        current_user: User,
    ) -> Reservas:
        return ReservasRepository.create_admin(session, reserva_in, current_user)

    # ============================================================
    # Listar reservas del usuario autenticado
    # ============================================================
    @staticmethod
    def get_mis_reservas(
        session: SessionDep,
        current_user: User,
        offset: int = 0,
        limit: int = 100,
    ):
        return ReservasRepository.list_by_user(session, current_user.id, offset, limit)

    # ============================================================
    # Listar reservas (ADMIN)
    # ============================================================
    @staticmethod
    def admin_list_reservas(
        session: SessionDep,
        offset: int = 0,
        limit: int = 100,
    ):
        return ReservasRepository.list_all(session, offset, limit)

    # ============================================================
    # Listar reservas por usuario (ADMIN)
    # ============================================================
    @staticmethod
    def admin_list_reservas_by_user(
        session: SessionDep,
        user_id: str,
    ):
        return ReservasRepository.list_by_user(session, user_id)

    # ============================================================
    # Obtener reserva por ID (ADMIN)
    # ============================================================
    @staticmethod
    def admin_get_reserva_by_id(
        session: SessionDep,
        reserva_id: int,
    ) -> Reservas:
        reserva = ReservasRepository.get_by_id(session, reserva_id)
        if not reserva:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        return reserva

    # ============================================================
    # Cancelar reserva (ADMIN)
    # ============================================================
    @staticmethod
    def admin_delete_reserva(
        session: SessionDep,
        reserva_id: int,
        current_user: User,
    ) -> Reservas:
        reserva_db = ReservasRepository.get_by_id(session, reserva_id)

        data = {
            "id_reserva_estado": ESTADO_RESERVA_CANCELADA,
            "updated_date": dt.datetime.now(),
            "fecha_modificacion_reserva": dt.datetime.now(),
            "id_usuario_updated": current_user.id,
        }

        return ReservasRepository.update(session, reserva_db, data)

    @staticmethod
    def create_reserva_from_metadata(session, payload: dict, stripe_session_obj: Optional[dict] = None) -> Reservas:
        """
        Create and persist a Reservas row using model column names.
        - Expects payload keys: 'tour_id' (or 'id_tour'), 'fecha_reserva' (ISO), 'numero_personas', 'user_email' (optional), 'nombre_cliente' (optional), 'email_cliente' (optional)
        - If `stripe_session_obj` is provided, use its customer details to fill missing name/email and to set checkout/payment ids.
        """
        # resolve tour id
        tour_id_raw = payload.get("tour_id") or payload.get("id_tour")
        if not tour_id_raw:
            raise ValueError("Missing tour_id in metadata")
        id_tour = int(tour_id_raw)

        # resolve user by email (optional)
        user_email = payload.get("user_email") or payload.get("email_cliente")
        user = None
        id_usuario = None
        if user_email:
            user = session.exec(select(User).where(User.email == user_email)).first()
            if user:
                id_usuario = getattr(user, "id", None)

        # customer name/email from payload or stripe session
        nombre_cliente = payload.get("nombre_cliente")
        email_cliente = payload.get("email_cliente") or user_email

        if stripe_session_obj and isinstance(stripe_session_obj, dict):
            cust = stripe_session_obj.get("customer_details", {}) or {}
            nombre_cliente = nombre_cliente or cust.get("name")
            email_cliente = email_cliente or cust.get("email") or stripe_session_obj.get("customer_email")

        # ensure non-null nombre_cliente to avoid DB NOT NULL violations
        if not nombre_cliente:
            nombre_cliente = "Cliente"

        # parse fecha_reserva
        fecha_iso = payload.get("fecha_reserva")
        fecha_reserva = None
        if fecha_iso:
            try:
                fecha_reserva = dt.datetime.fromisoformat(fecha_iso)
            except Exception:
                try:
                    d = dt.date.fromisoformat(fecha_iso)
                    fecha_reserva = dt.datetime.combine(d, dt.time())
                except Exception:
                    fecha_reserva = None

        numero_personas = int(payload.get("numero_personas", 1))

        reserva = Reservas(
            id_tour=id_tour,
            id_usuario=id_usuario,
            nombre_cliente=nombre_cliente,
            email_cliente=email_cliente,
            numero_personas=numero_personas,
            fecha_reserva=fecha_reserva,
            created_date=dt.datetime.now(),
            updated_date=dt.datetime.now(),
        )

        # attach stripe ids if present in session object
        if stripe_session_obj and isinstance(stripe_session_obj, dict):
            checkout_id = stripe_session_obj.get("id")
            if checkout_id:
                reserva.checkout_session_id = checkout_id
            # sometimes payment_intent is nested
            payment_intent = stripe_session_obj.get("payment_intent") or stripe_session_obj.get("payment_intent_id")
            if payment_intent:
                reserva.payment_intent_id = payment_intent

        session.add(reserva)
        session.commit()
        session.refresh(reserva)
        return reserva
    # ============================================================
    # Actualizar reserva (ADMIN)
    # ============================================================
    @staticmethod
    def admin_update_reserva(
        session: SessionDep,
        reserva_id: int,
        reserva_in: ReservasUpdate,
        current_user: User,
    ) -> Reservas:
        reserva_db = ReservasRepository.get_by_id(session, reserva_id)

        update_data = reserva_in.model_dump(exclude_unset=True)
        update_data["id_usuario_updated"] = current_user.id
        update_data["updated_date"] = dt.datetime.now()
        update_data["fecha_modificacion_reserva"] = dt.datetime.now()

        return ReservasRepository.update(session, reserva_db, update_data)

    # ============================================================
    # Marcar como PAGADA (ADMIN)
    # ============================================================
    @staticmethod
    def admin_pagar_reserva(
        session: SessionDep,
        reserva_id: int,
        current_user: User,
    ) -> Reservas:
        reserva_db = ReservasRepository.get_by_id(session, reserva_id)

        if not reserva_db:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")

        data = {
            "id_reserva_estado": ESTADO_RESERVA_PAGADA,
            "updated_date": dt.datetime.now(),
            "fecha_modificacion_reserva": dt.datetime.now(),
            "id_usuario_updated": current_user.id,
        }

        return ReservasRepository.update(session, reserva_db, data)
