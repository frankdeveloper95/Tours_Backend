import datetime
from sqlmodel import select
from fastapi import HTTPException
from sqlalchemy.orm import selectinload

from app.auth.deps import SessionDep
from app.models import Tour, User, Guia


class ToursRepository:
    @staticmethod
    def list(session: SessionDep, offset: int = 0, limit: int = 100):
        stmt = (
            select(Tour)
            .options(
                selectinload(Tour.operadora),
                selectinload(Tour.guia).selectinload(Guia.usuario),
            )
            .offset(offset)
            .limit(limit)
        )
        return session.exec(stmt).all()

    @staticmethod
    def get_by_id(session: SessionDep, tour_id: int) -> Tour:
        stmt = (
            select(Tour)
            .where(Tour.id == tour_id)
            .options(
                selectinload(Tour.operadora),
                selectinload(Tour.guia).selectinload(Guia.usuario),
            )
        )
        tour = session.exec(stmt).first()

        if not tour:
            raise HTTPException(status_code=404, detail="Tour no encontrado")

        return tour

    @staticmethod
    def create(session: SessionDep, tour: Tour) -> Tour:
        session.add(tour)
        session.commit()
        session.refresh(tour)
        return tour

    @staticmethod
    def update(session: SessionDep, tour_db: Tour, data: dict, user: User) -> Tour:
        tour_db.sqlmodel_update(
            data,
            update={
                "id_usuario_updated": user.id,
                "updated_date": datetime.datetime.now()
            }
        )
        session.add(tour_db)
        session.commit()
        session.refresh(tour_db)
        return tour_db

    @staticmethod
    def hard_delete(session: SessionDep, tour_db: Tour) -> None:
        session.delete(tour_db)
        session.commit()
