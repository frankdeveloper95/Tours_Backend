import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel import select

from app.api.deps import get_current_active_superuser, SessionDep
from app.models import Reservas, ReservasCreate, User, ReservasUpdate

router = APIRouter(tags=["reservas"], dependencies=[Depends(get_current_active_superuser)])


@router.get("/reserva", response_model=list[Reservas])
async def get_reservas(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100
):
    reservas = session.exec(select(Reservas).offset(offset).limit(limit)).all()
    return reservas


@router.get("/reserva/{id}", response_model=Reservas)
async def get_reservas_by_id(
        id: int,
        session: SessionDep
):
    reservas = session.get(Reservas, id)
    if not reservas:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reservas


@router.post("/reserva", response_model=Reservas)
async def create_reserva(
        reserva_in: ReservasCreate,
        session: SessionDep,
        current_user: User = Depends(get_current_active_superuser)
):
    user = session.get(User, reserva_in.id_usuario)
    reserva = Reservas.model_validate(reserva_in, update={
        "id_usuario_created": current_user.id,
        "nombre_cliente": user.nombre + " " + user.apellido,
        "email_cliente": user.email,
        "fecha_reserva": datetime.datetime.now()
    })
    session.add(reserva)
    session.commit()
    session.refresh(reserva)
    return reserva


@router.put("/reserva/{id}", response_model=Reservas)
async def update_reserva(
        id: int,
        reserva: ReservasUpdate,
        session: SessionDep,
        current_user: User = Depends(get_current_active_superuser)
):
    reserva_db = session.get(Reservas, id)
    if not reserva_db:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    reserva_data = reserva.model_dump(exclude_unset=True)
    reserva_db.sqlmodel_update(
        reserva_data,
        update={
            "id_usuario_updated": current_user.id,
            "updated_date": datetime.datetime.now(),
            "fecha_modificacion_reserva": datetime.datetime.now()
        }
    )
    session.add(reserva_db)
    session.commit()
    session.refresh(reserva_db)
    return reserva_db

@router.delete("/reserva/{id}")
async def delete_reserva(
        id: int,
        session: SessionDep
):
    reserva = session.get(Reservas, id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    session.delete(reserva)
    session.commit()
    return JSONResponse(content={"message": "Reserva eliminada", "Operadora": jsonable_encoder(reserva)})