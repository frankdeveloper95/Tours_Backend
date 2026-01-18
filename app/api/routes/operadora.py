import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel import select

from app.auth.deps import get_current_active_superuser, SessionDep
from app.models import Operadora, OperadoraCreate, User, OperadoraOut, OperadoraUpdate

router = APIRouter(tags=["operadora"], dependencies=[Depends(get_current_active_superuser)])


@router.post("/operadora", response_model=OperadoraOut)
async def add_operadora(
        operadora_in: OperadoraCreate,
        session: SessionDep,
        current_user: User = Depends(get_current_active_superuser)
):
    operadora = Operadora.model_validate(operadora_in, update={"id_usuario_created": current_user.id})
    session.add(operadora)
    session.commit()
    session.refresh(operadora)
    return operadora


@router.get("/operadora", response_model=list[OperadoraOut])
async def get_operadora(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
):
    operadoras = session.exec(select(Operadora).offset(offset).limit(limit)).all()
    return operadoras


@router.get("/operadora/{operadora_id}", response_model=OperadoraOut)
async def get_operadora_by_id(operadora_id: int, session: SessionDep):
    operadora = session.get(Operadora, operadora_id)
    if not operadora:
        raise HTTPException(status_code=404, detail="Operadora not encontrada")
    return operadora


@router.put("/operadora/{operadora_id}", response_model=OperadoraOut)
async def update_operadora(
        operadora_id: int, operadora: OperadoraUpdate, session: SessionDep,
        current_user: User = Depends(get_current_active_superuser)
):
    operadora_db = session.get(Operadora, operadora_id)
    if not operadora_db:
        raise HTTPException(status_code=404, detail="Operadora not encontrada")
    operadora_data = operadora.model_dump(exclude_unset=True)
    operadora_db.sqlmodel_update(
        operadora_data,
        update=
        {"id_usuario_updated": current_user.id,
         "updated_date": datetime.datetime.now()
         }
    )
    session.add(operadora_db)
    session.commit()
    session.refresh(operadora_db)
    return operadora_db


@router.delete("/operadora/{operadora_id}")
async def delete_operadora(
        operadora_id: int,
        session: SessionDep,
):
    operadora = session.get(Operadora, operadora_id)
    if not operadora:
        raise HTTPException(status_code=404, detail="No se encontro operadora")
    session.delete(operadora)
    session.commit()
    return JSONResponse(content={"message": "Operadora eliminada", "Operadora": jsonable_encoder(operadora)})
