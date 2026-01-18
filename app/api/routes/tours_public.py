from typing import Annotated
from fastapi import APIRouter
from fastapi.params import Query

from app.auth.deps import SessionDep
from app.models import TourPublic
from app.tours.service import ToursService

router = APIRouter(prefix="/tours", tags=["Tours"])

@router.get("", response_model=list[TourPublic])
async def get_tours(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return ToursService.get_tours(session, offset, limit)

@router.get("/{id}", response_model=TourPublic)
async def get_tour_by_id(id: int, session: SessionDep):
    return ToursService.get_tour(session, id)
