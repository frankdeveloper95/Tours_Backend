import datetime as dt
from fastapi import HTTPException

from app.auth.deps import SessionDep
from app.models import Reservas, ReservasCreatePublic, ReservasUpdate, User
from app.reservas.repository import ReservasRepository


# Opcional: podrías mover esto a un módulo de constantes o Enum
ESTADO_RESERVA_PENDIENTE = 2   # pendiente de pago / confirmación
ESTADO_RESERVA_CANCELADA = 3   # cancelada
# ESTADO_RESERVA_PAGADA = 4    # por ejemplo, para cuando integremos Stripe


class ReservasService:
    @staticmethod
    def create_reserva(
        session: SessionDep,
        reserva_in: ReservasCreatePublic,
        current_user: User,
    ) -> Reservas:
        tour = ReservasRepository.get_tour(session, reserva_in.id_tour)

        # Validación básica de cantidad
        cantidad = reserva_in.numero_personas
        if cantidad <= 0:
            raise HTTPException(status_code=400, detail="Número de personas inválido")

        if tour.capacidad_maxima is not None and cantidad > tour.capacidad_maxima:
            raise HTTPException(
                status_code=400,
                detail="La cantidad supera la capacidad máxima del tour",
            )

        # (Opcional) Validar que el tour esté activo
        if hasattr(tour, "activo") and not tour.activo:
            raise HTTPException(status_code=400, detail="El tour no está disponible")

        # (Opcional) Validar fecha de reserva
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

    @staticmethod
    def get_mis_reservas(
        session: SessionDep,
        current_user: User,
        offset: int = 0,
        limit: int = 100,
    ):
        return ReservasRepository.list_by_user(session, current_user.id, offset, limit)

    @staticmethod
    def admin_list_reservas(
        session: SessionDep,
        offset: int = 0,
        limit: int = 100,
    ):
        return ReservasRepository.list_all(session, offset, limit)

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
