from typing import Annotated
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.auth.deps import SessionDep, get_current_active_superuser
from app.models import (
    ReservasCreateAdmin,
    User,
    ReservasUpdate,
    ReservasAdminRead
)
from app.reservas.service import ReservasService

router = APIRouter(
    prefix="/admin/reservas",
    tags=["Admin Reservas"],
)

# ============================================================
# Crear reserva desde admin
# ============================================================
@router.post("", response_model=ReservasAdminRead)
async def create_reserva_admin(
    reserva_in: ReservasCreateAdmin,
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
):
    return ReservasService.create_reserva_admin(session, reserva_in, current_user)


# ============================================================
# Listar reservas por usuario (ADMIN)
# (IMPORTANTE: va antes de /{id})
# ============================================================
@router.get("/usuario/{user_id}", response_model=list[ReservasAdminRead])
async def get_reservas_by_user(
    user_id: str,
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
):
    return ReservasService.admin_list_reservas_by_user(session, user_id)


# ============================================================
# Listar reservas (ADMIN)
# ============================================================
@router.get("", response_model=list[ReservasAdminRead])
async def get_reservas(
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
    usuario_id: str | None = None,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
):
    if usuario_id:
        return ReservasService.admin_list_reservas_by_user(session, usuario_id)

    return ReservasService.admin_list_reservas(session, offset, limit)


# ============================================================
# Obtener reserva por ID (ADMIN)
# ============================================================
@router.get("/{id}", response_model=ReservasAdminRead)
async def get_reserva_by_id(
    id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
):
    return ReservasService.admin_get_reserva_by_id(session, id)


# ============================================================
# Eliminar (cancelar) reserva
# ============================================================
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


# ============================================================
# Actualizar reserva
# ============================================================
@router.put("/{id}", response_model=ReservasAdminRead)
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


# ============================================================
# Marcar como pagada
# ============================================================
@router.patch("/{reserva_id}/pagar", response_model=ReservasAdminRead)
async def admin_pagar_reserva(
    reserva_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
):
    return ReservasService.admin_pagar_reserva(session, reserva_id, current_user)
