from typing import Annotated
from fastapi import APIRouter, Depends, Query

from app.auth.deps import SessionDep, get_current_active_user
from app.models import Reservas, ReservasCreatePublic, User, ReservasPublic
from app.reservas.service import ReservasService

router = APIRouter(prefix="/reservas", tags=["Reservas"])


@router.post("", response_model=Reservas)
async def create_reserva(
    reserva_in: ReservasCreatePublic,
    session: SessionDep,
    current_user: User = Depends(get_current_active_user),
):
    return ReservasService.create_reserva_public(session, reserva_in, current_user)


@router.get("/me/{current_user}", response_model=list[ReservasPublic])
async def get_mis_reservas(
    session: SessionDep,
    current_user: User = Depends(get_current_active_user),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
):
    return ReservasService.get_mis_reservas(session, current_user, offset, limit)
