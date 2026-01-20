import datetime
from sqlmodel import select
from fastapi import HTTPException
from sqlalchemy.orm import selectinload

from app.auth.deps import SessionDep
from app.models import Tour, User, Guia


class ToursRepository:
    @staticmethod
    def list(session: SessionDep, offset: int = 0, limit: int = 100, is_active: bool | None = None):
        stmt = (
            select(Tour)
            .options(
                selectinload(Tour.operadora),
                selectinload(Tour.guia).selectinload(Guia.usuario),
            )
        )

        if is_active is not None:
            stmt = stmt.where(Tour.is_active == is_active)

        stmt = stmt.offset(offset).limit(limit)

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
    def update(session: SessionDep, tour_db: Tour, data: dict, user: User | None = None) -> Tour:
        # Si viene user, agregamos metadata de actualización
        update_meta = {
            "updated_date": datetime.datetime.now()
        }

        if user:
            update_meta["id_usuario_updated"] = user.id

        tour_db.sqlmodel_update(
            data,
            update=update_meta
        )

        session.add(tour_db)
        session.commit()
        session.refresh(tour_db)
        return tour_db

    @staticmethod
    def hard_delete(session: SessionDep, tour_db: Tour) -> None:
        session.delete(tour_db)
        session.commit()

    