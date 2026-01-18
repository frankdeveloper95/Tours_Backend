from typing import Annotated
from fastapi import Query

from app.auth.deps import SessionDep
from app.models import TourCreate, TourUpdate, Tour, User
from app.tours.repository import ToursRepository
import datetime as dt


class ToursService:
    @staticmethod
    def get_tours(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
    ):
        # El repo debe retornar tours con relaciones (operadora/guia) si tu TourPublic las necesita.
        return ToursRepository.list(session, offset, limit)

    @staticmethod
    def get_tour(session: SessionDep, tour_id: int):
        return ToursRepository.get_by_id(session, tour_id)

    @staticmethod
    def create_tour(session: SessionDep, tour_in: TourCreate, current_user: User):
        # ✅ setear auditoría
        tour = Tour.model_validate(
            tour_in,
            update={
                "id_usuario_created": current_user.id,
                "created_date": dt.datetime.now()
            }
        )
        return ToursRepository.create(session, tour)

    @staticmethod
    def update_tour(session: SessionDep, tour_id: int, tour_in: TourUpdate, current_user: User):
        tour_db = ToursRepository.get_by_id(session, tour_id)

        # ✅ update parcial
        data = tour_in.model_dump(exclude_unset=True)

        # ✅ no permitir None en listas JSONB (si el frontend manda null, evita pisar)
        list_fields = {"incluye", "no_incluye", "que_llevar", "itinerario"}
        for f in list_fields:
            if f in data and data[f] is None:
                data.pop(f)

        # ✅ auditoría correcta
        data["id_usuario_updated"] = current_user.id
        data["updated_date"] = dt.datetime.now()

        return ToursRepository.update(session, tour_db, data, current_user)

    @staticmethod
    def delete_tour_hard(session: SessionDep, tour_id: int):
        tour_db = ToursRepository.get_by_id(session, tour_id)
        ToursRepository.hard_delete(session, tour_db)
        return tour_db
