from typing import Annotated
from fastapi import Query, HTTPException

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
        return ToursRepository.list(session, offset, limit)

    @staticmethod
    def get_tour(session: SessionDep, tour_id: int):
        return ToursRepository.get_by_id(session, tour_id)

    SPONDYLUS_OPERADORA_ID = 12  

    @staticmethod
    def create_tour(session: SessionDep, tour_in: TourCreate, current_user: User):

        # ---------------------------------------------------------
        # 1️⃣ Forzar operadora Spondylus Tour SIEMPRE
        # ---------------------------------------------------------
        tour_in.id_operadora = ToursService.SPONDYLUS_OPERADORA_ID

        # ---------------------------------------------------------
        # 2️⃣ Asignar usuario creador
        # ---------------------------------------------------------
        tour_in.id_usuario_created = current_user.id

        # ---------------------------------------------------------
        # 3️⃣ Imagen por defecto si viene vacía
        # ---------------------------------------------------------
        if not tour_in.image_url:
            tour_in.image_url = "https://placehold.co/600x400?text=Tour"

        # ---------------------------------------------------------
        # 4️⃣ Crear instancia del modelo Tour
        # ---------------------------------------------------------
        tour = Tour.model_validate(
            tour_in,
            update={
                "created_date": dt.datetime.now()
            }
        )

        # ---------------------------------------------------------
        # 5️⃣ Guardar en BD
        # ---------------------------------------------------------
        return ToursRepository.create(session, tour)


    @staticmethod
    def update_tour(session: SessionDep, tour_id: int, tour_in: TourUpdate, current_user: User):
        tour_db = ToursRepository.get_by_id(session, tour_id)

        data = tour_in.model_dump(exclude_unset=True)

        # Evitar pisar listas JSONB con null
        list_fields = {"incluye", "no_incluye", "que_llevar", "itinerario"}
        for f in list_fields:
            if f in data and data[f] is None:
                data.pop(f)

        data["id_usuario_updated"] = current_user.id
        data["updated_date"] = dt.datetime.now()

        return ToursRepository.update(session, tour_db, data, current_user)

    @staticmethod
    def delete_tour_hard(session: SessionDep, tour_id: int):
        tour_db = ToursRepository.get_by_id(session, tour_id)
        ToursRepository.hard_delete(session, tour_db)
        return tour_db
