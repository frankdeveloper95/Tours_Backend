import uuid
from sqlmodel import select
from fastapi import HTTPException

from app.auth.deps import SessionDep
from app.models import Reservas, Tour


class ReservasRepository:
    @staticmethod
    def get_by_id(session: SessionDep, reserva_id: int) -> Reservas:
        reserva = session.get(Reservas, reserva_id)
        if not reserva:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        return reserva

    @staticmethod
    def list_all(session: SessionDep, offset: int = 0, limit: int = 100):
        return session.exec(
            select(Reservas)
            .order_by(Reservas.created_date.desc())  # ✅ orden más reciente primero
            .offset(offset)
            .limit(limit)
        ).all()

    @staticmethod
    def list_by_user(session: SessionDep, user_id: uuid.UUID, offset: int = 0, limit: int = 100):
        return session.exec(
            select(Reservas)
            .where(Reservas.id_usuario == user_id)
            .order_by(Reservas.created_date.desc())  # ✅ orden más reciente primero
            .offset(offset)
            .limit(limit)
        ).all()

    @staticmethod
    def create(session: SessionDep, reserva: Reservas) -> Reservas:
        session.add(reserva)
        session.commit()
        session.refresh(reserva)
        return reserva

    @staticmethod
    def update(session: SessionDep, reserva_db: Reservas, update_data: dict) -> Reservas:
        for key, value in update_data.items():
            setattr(reserva_db, key, value)

        session.add(reserva_db)
        session.commit()
        session.refresh(reserva_db)
        return reserva_db

    @staticmethod
    def hard_delete(session: SessionDep, reserva_db: Reservas) -> None:
        session.delete(reserva_db)
        session.commit()

    @staticmethod
    def get_tour(session: SessionDep, tour_id: int) -> Tour:
        tour = session.get(Tour, tour_id)
        if not tour:
            raise HTTPException(status_code=404, detail="Tour no encontrado")
        return tour

    @staticmethod
    def update(session: SessionDep, reserva_db: Reservas, data: dict) -> Reservas:
        for key, value in data.items():
            setattr(reserva_db, key, value)

        session.add(reserva_db)
        session.commit()
        session.refresh(reserva_db)
        return reserva_db
