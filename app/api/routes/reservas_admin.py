from typing import Annotated
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.auth.deps import SessionDep, get_current_active_superuser
from app.models import Reservas, ReservasCreateAdmin, User, ReservasUpdate
from app.reservas.service import ReservasService

router = APIRouter(
    prefix="/admin/reservas",
    tags=["Admin Reservas"],
)


@router.post("", response_model=Reservas)
async def create_reserva_admin(
    reserva_in: ReservasCreateAdmin,
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
):
    return ReservasService.create_reserva_admin(session, reserva_in, current_user)


@router.get("", response_model=list[Reservas])
async def get_reservas(
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
):
    return ReservasService.admin_list_reservas(session, offset, limit)


@router.delete("/{id}")
async def delete_reserva(
    id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
):
    deleted = ReservasService.admin_delete_reserva(session, id, current_user)
    return JSONResponse(content={
        "message": "Reserva cancelada",
        "reserva": jsonable_encoder(deleted)
    })

@router.put("/{id}", response_model=Reservas)
async def update_reserva(
    id: int,
    reserva_in: ReservasUpdate,
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
):
    return ReservasService.admin_update_reserva(
        session=session,
        reserva_id=id,
        reserva_in=reserva_in,
        current_user=current_user,
    )