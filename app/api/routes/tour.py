import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.params import Query

from app.api.deps import get_current_active_superuser
from app.models import TourCreate, User, Tour, TourUpdate
from app.api.deps import SessionDep
from sqlmodel import select

router = APIRouter(tags=["Tours"], dependencies=[Depends(get_current_active_superuser)])


@router.post("/tour", response_model=Tour)
async def create_tour(
        tour_in: TourCreate,
        session: SessionDep,
        current_user: User = Depends(get_current_active_superuser)
):
    tour = Tour.model_validate(tour_in, update={"id_usuario_created": current_user.id})
    session.add(tour)
    session.commit()
    session.refresh(tour)
    return tour


@router.get("/tour", response_model=list[Tour])
async def get_tours(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
):
    tours = session.exec(select(Tour).offset(offset).limit(limit)).all()
    return tours


@router.put("/tour/{id}", response_model=Tour)
async def update_tour(
        id: int,
        tour: TourUpdate,
        session: SessionDep,
        current_user: User = Depends(get_current_active_superuser)
):
    tour_db = session.get(Tour, id)
    if not tour_db:
        raise HTTPException(status_code=404, detail="Tour no encontrado")
    tour_data = tour.model_dump(exclude_unset=True)
    tour_db.sqlmodel_update(
        tour_data,
        update={
            "id_usuario_updated": current_user.id,
            "updated_date": datetime.datetime.now()
        }
    )
    session.add(tour_db)
    session.commit()
    session.refresh(tour_db)
    return tour_db


@router.get("/tour/{id}", response_model=Tour)
async def get_tour_by_id(
        id: int,
        session: SessionDep
):
    tour = session.get(Tour, id)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour no encontrado")
    return tour


@router.delete("/tour/{id}")
async def delete_tour(
        id: int,
        session: SessionDep
):
    tour = session.get(Tour, id)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour no encontrado")
    session.delete(tour)
    session.commit()
    return JSONResponse(content={"message": "Tour eliminado correctamente", "Guia": jsonable_encoder(tour)})
