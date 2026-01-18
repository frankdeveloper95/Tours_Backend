from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.auth.deps import SessionDep, get_current_active_superuser
from app.models import TourCreate, TourUpdate, Tour, User
from app.tours.service import ToursService

router = APIRouter(
    prefix="/admin/tours",
    tags=["Admin Tours"],
    dependencies=[Depends(get_current_active_superuser)]
)

@router.post("/", response_model=Tour)
async def create_tour(
    tour_in: TourCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
):
    return ToursService.create_tour(session, tour_in, current_user)

@router.put("/{id}", response_model=Tour)
async def update_tour(
    id: int,
    tour_in: TourUpdate,
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
):
    return ToursService.update_tour(session, id, tour_in, current_user)

@router.delete("/{id}")
async def delete_tour(id: int, session: SessionDep):
    deleted = ToursService.delete_tour_hard(session, id)
    return JSONResponse(content={
        "message": "Tour eliminado correctamente",
        "tour": jsonable_encoder(deleted)
    })
