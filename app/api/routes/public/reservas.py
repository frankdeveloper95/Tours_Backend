from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.api.deps import get_current_active_user, SessionDep
from app.models import Reservas, User, ReservasPublic

router = APIRouter(tags=["public"], dependencies=[Depends(get_current_active_user)])


@router.get("/reservas", response_model=list[ReservasPublic])
async def get_reservas(
        session: SessionDep,
        current_user: User = Depends(get_current_active_user)
):
    statement = select(Reservas).where(Reservas.id_usuario == current_user.id)
    reservas = session.exec(statement).all()
    if not reservas:
        raise HTTPException(status_code=404, detail="No tienes reservas")
    return reservas
