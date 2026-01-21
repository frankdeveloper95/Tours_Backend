import datetime as dt
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
