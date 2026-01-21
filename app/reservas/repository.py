import uuid
from sqlmodel import select
from fastapi import HTTPException
from sqlalchemy.orm import selectinload

from app.auth.deps import SessionDep
from app.models import Reservas, Tour


class ReservasRepository:

    # ============================================================
    # Obtener reserva por ID
    # ============================================================
    @staticmethod
    def get_by_id(session: SessionDep, reserva_id: int) -> Reservas:
        reserva = session.exec(
            select(Reservas)
            .where(Reservas.id == reserva_id)
            .options(
                selectinload(Reservas.tour),
                selectinload(Reservas.estado)
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
                selectinload(Reservas.estado)
            )
            .order_by(Reservas.created_date.desc())
            .offset(offset)
            .limit(limit)
        ).all()

    # ============================================================
    # Listar reservas por usuario
    # ============================================================
    @staticmethod
    def list_by_user(session: SessionDep, user_id: uuid.UUID, offset: int = 0, limit: int = 100) -> list[Reservas]:
        return session.exec(
            select(Reservas)
            .where(Reservas.id_usuario == user_id)
            .options(
                selectinload(Reservas.tour),
                selectinload(Reservas.estado)
            )
            .order_by(Reservas.created_date.desc())
            .offset(offset)
            .limit(limit)
        ).all()

    # Alias
    @staticmethod
    def get_by_user(session: SessionDep, user_id: uuid.UUID) -> list[Reservas]:
        return ReservasRepository.list_by_user(session, user_id)

    # ============================================================
    # Crear reserva
    # ============================================================
    @staticmethod
    def create(session: SessionDep, reserva: Reservas) -> Reservas:
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
