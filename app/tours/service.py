from typing import Annotated
from fastapi import HTTPException

from app.auth.deps import SessionDep
from app.models import TourCreate, TourUpdate, Tour, User
from app.tours.repository import ToursRepository
import datetime as dt


class ToursService:

    # ============================================================
    # LISTAR TOURS (ADMIN o PUBLIC)
    # ============================================================
    @staticmethod
    def get_tours(
        session: SessionDep,
        offset: int = 0,
        limit: int = 100,
        is_active: bool | None = None
    ):
        """
        - ADMIN → is_active=None → devuelve todos
        - PUBLIC → is_active=True → solo activos
        """
        return ToursRepository.list(session, offset, limit, is_active)


    # ============================================================
    # OBTENER TOUR POR ID
    # ============================================================
    @staticmethod
    def get_tour(session: SessionDep, tour_id: int):
        return ToursRepository.get_by_id(session, tour_id)

    SPONDYLUS_OPERADORA_ID = 12  

    # ============================================================
    # CREAR TOUR
    # ============================================================
    @staticmethod
    def create_tour(session: SessionDep, tour_in: TourCreate, current_user: User):

        tour_in.id_operadora = ToursService.SPONDYLUS_OPERADORA_ID
        tour_in.id_usuario_created = current_user.id

        if not tour_in.image_url:
            tour_in.image_url = "https://placehold.co/600x400?text=Tour"

        # 🔥 FIX: Normalizar fecha para evitar desfase por timezone
        if isinstance(tour_in.fecha, dt.datetime):
            tour_in.fecha = tour_in.fecha.date()

        tour = Tour.model_validate(
            tour_in,
            update={"created_date": dt.datetime.now()}
        )

        print("✅ Tour creado:", tour)
        return ToursRepository.create(session, tour)


    # ============================================================
    # ACTUALIZAR TOUR
    # ============================================================
    @staticmethod
    def update_tour(session: SessionDep, tour_id: int, tour_in: TourUpdate, current_user: User):
        tour_db = ToursRepository.get_by_id(session, tour_id)

        data = tour_in.model_dump(exclude_unset=True)

        # 🔥 FIX: Normalizar fecha para evitar desfase por timezone
        if "fecha" in data:
            if isinstance(data["fecha"], dt.datetime):
                data["fecha"] = data["fecha"].date()

        # Evitar pisar listas JSONB con null
        list_fields = {"incluye", "no_incluye", "que_llevar", "itinerario"}
        for f in list_fields:
            if f in data and data[f] is None:
                data.pop(f)

        data["id_usuario_updated"] = current_user.id
        data["updated_date"] = dt.datetime.now()

        return ToursRepository.update(session, tour_db, data, current_user)



    # ============================================================
    # DESACTIVAR TOUR (Soft Delete)
    # ============================================================
    @staticmethod
    def deactivate_tour(session: SessionDep, tour_id: int):
        tour_db = ToursRepository.get_by_id(session, tour_id)

        if not tour_db:
            raise HTTPException(status_code=404, detail="Tour no encontrado")

        if not tour_db.is_active:
            raise HTTPException(status_code=400, detail="El tour ya está desactivado")

        data = {
            "is_active": False,
            "updated_date": dt.datetime.now()
        }

        return ToursRepository.update(session, tour_db, data)

    # ============================================================
    # ACTIVAR TOUR
    # ============================================================
    @staticmethod
    def activate_tour(session: SessionDep, tour_id: int):
        tour_db = ToursRepository.get_by_id(session, tour_id)

        if not tour_db:
            raise HTTPException(status_code=404, detail="Tour no encontrado")

        if tour_db.is_active:
            raise HTTPException(status_code=400, detail="El tour ya está activo")

        data = {
            "is_active": True,
            "updated_date": dt.datetime.now()
        }

        return ToursRepository.update(session, tour_db, data)
