import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel import select

from app.auth.deps import SessionDep
from app.auth.deps import get_current_active_superuser
from app.models import Guia, GuiaCreate, User, GuiaWithUser, GuiaUpdate

router = APIRouter(tags=["guia"], dependencies=[Depends(get_current_active_superuser)])


@router.post("/guia", response_model=Guia)
async def add_guia(
        guia_in: GuiaCreate,
        session: SessionDep,
        current_user: User = Depends(get_current_active_superuser)
):
    guia = Guia.model_validate(guia_in, update={"id_usuario_created": current_user.id})
    session.add(guia)
    session.commit()
    session.refresh(guia)
    return guia


@router.get("/guia", response_model=list[GuiaWithUser])
async def get_guia(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
):
    guias = session.exec(select(Guia).offset(offset).limit(limit)).all()
    return guias


@router.get("/guia/{id}", response_model=GuiaWithUser)
async def get_guia_by_id(
        id: int,
        session: SessionDep,
):
    guia = session.get(Guia, id)
    if not guia:
        raise HTTPException(status_code=404, detail="Guia no encontrado")
    return guia


@router.put("/guia/{id}", response_model=Guia)
async def update_guia(
        id: int,
        guia: GuiaUpdate,
        session: SessionDep,
        current_user: User = Depends(get_current_active_superuser)
):
    guia_db = session.get(Guia, id)
    if not guia_db:
        raise HTTPException(status_code=404, detail="Guia no encontrado")
    guia_data = guia.model_dump(exclude_unset=True)
    guia_db.sqlmodel_update(
        guia_data,
        update={
            "id_usuario_updated": current_user.id,
            "updated_date": datetime.datetime.now()
        }
    )
    session.add(guia_db)
    session.commit()
    session.refresh(guia_db)
    return guia_db


@router.delete("/guia/{id}")
async def delete_guia(
        id: int,
        session: SessionDep,
):
    guia = session.get(Guia, id)
    if not guia:
        raise HTTPException(status_code=404, detail="Guia no encontrado")
    session.delete(guia)
    session.commit()
    return JSONResponse(content={"message": "Guia eliminado", "Guia": jsonable_encoder(guia)})
