import uuid
from sqlmodel import select
from fastapi import HTTPException
from sqlalchemy.orm import selectinload

from app.auth.deps import SessionDep
from app.models import Reservas, Tour, ReservasCreateAdmin, User


class ReservasRepository:

    # ============================================================
    # Obtener reserva por ID (con relaciones completas)
    # ============================================================
    @staticmethod
    def get_by_id(session: SessionDep, reserva_id: int) -> Reservas:
        reserva = session.exec(
            select(Reservas)
            .where(Reservas.id == reserva_id)
            .options(
                selectinload(Reservas.tour),
                selectinload(Reservas.estado),
                selectinload(Reservas.usuario),
                selectinload(Reservas.usuario_created),
                selectinload(Reservas.usuario_updated),
            )
        ).first()

        if not reserva:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")

        return reserva

    # ============================================================
    # Listar TODAS las reservas (admin)
    # ============================================================
    @staticmethod
    def list_all(session: SessionDep, offset: int = 0, limit: int = 100) -> list[Reservas]:
        return session.exec(
            select(Reservas)
            .options(
                selectinload(Reservas.tour),
                selectinload(Reservas.estado),
                selectinload(Reservas.usuario),
                selectinload(Reservas.usuario_created),
                selectinload(Reservas.usuario_updated),
            )
            .order_by(Reservas.created_date.desc())
            .offset(offset)
            .limit(limit)
        ).all()

    # ============================================================
    # Listar reservas por usuario (ADMIN)
    # Acepta str o uuid.UUID
    # ============================================================
    @staticmethod
    def list_by_user(session: SessionDep, user_id, offset: int = 0, limit: int = 100) -> list[Reservas]:

        # Convertir a UUID si viene como string
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="ID de usuario inválido")

        return session.exec(
            select(Reservas)
            .where(Reservas.id_usuario == user_id)
            .options(
                selectinload(Reservas.tour),
                selectinload(Reservas.estado),
                selectinload(Reservas.usuario),
                selectinload(Reservas.usuario_created),
                selectinload(Reservas.usuario_updated),
            )
            .order_by(Reservas.created_date.desc())
            .offset(offset)
            .limit(limit)
        ).all()

    # Alias
    @staticmethod
    def get_by_user(session: SessionDep, user_id) -> list[Reservas]:
        return ReservasRepository.list_by_user(session, user_id)

    # ============================================================
    # Crear reserva pública
    # ============================================================
    @staticmethod
    def create(session: SessionDep, reserva: Reservas) -> Reservas:
        session.add(reserva)
        session.commit()
        session.refresh(reserva)
        return reserva

    # ============================================================
    # Crear reserva desde ADMIN
    # ============================================================
    @staticmethod
    def create_admin(session: SessionDep, reserva_in: ReservasCreateAdmin, current_user: User) -> Reservas:

        reserva = Reservas(
            id_tour=reserva_in.id_tour,
            id_usuario=reserva_in.id_usuario,
            id_reserva_estado=reserva_in.id_reserva_estado,
            nombre_cliente=reserva_in.nombre_cliente,
            email_cliente=reserva_in.email_cliente,
            numero_personas=reserva_in.numero_personas,
            fecha_reserva=reserva_in.fecha_reserva,
            created_date=reserva_in.created_date,
            id_usuario_created=current_user.id,
        )

        session.add(reserva)
        session.commit()
        session.refresh(reserva)
        return reserva

    # ============================================================
    # Actualizar reserva
    # ============================================================
    @staticmethod
    def update(session: SessionDep, reserva_db: Reservas, data: dict) -> Reservas:
        for key, value in data.items():
            setattr(reserva_db, key, value)

        session.add(reserva_db)
        session.commit()
        session.refresh(reserva_db)
        return reserva_db

    # ============================================================
    # Obtener tour asociado
    # ============================================================
    @staticmethod
    def get_tour(session: SessionDep, tour_id: int) -> Tour:
        tour = session.get(Tour, tour_id)
        if not tour:
            raise HTTPException(status_code=404, detail="Tour no encontrado")
        return tour

    # ============================================================
    # Hard delete
    # ============================================================
    @staticmethod
    def _hard_delete(session: SessionDep, reserva_db: Reservas) -> None:
        session.delete(reserva_db)
        session.commit()
