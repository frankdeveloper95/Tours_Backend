import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel import select

from app.api.deps import SessionDep
from app.api.deps import get_current_active_superuser
from app.models import Zarpe, ZarpeCreate, User, ZarpeUpdate

router = APIRouter(tags=['zarpe'], dependencies=[Depends(get_current_active_superuser)])


@router.get("/zarpe", response_model=list[Zarpe])
async def get_zarpe(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
):
    zarpes = session.exec(select(Zarpe).offset(offset).limit(limit)).all()
    return zarpes


@router.get('/zarpe/{id}', response_model=Zarpe)
async def get_zarpe_by_id(
        id: int,
        session: SessionDep
):
    zarpe = session.get(Zarpe, id)
    if not zarpe:
        raise HTTPException(status_code=404, detail="No se encontro Zarpe")
    return zarpe


@router.post('/zarpe', response_model=Zarpe)
async def create_zarpe(
        zarpe_in: ZarpeCreate,
        session: SessionDep,
        current_user: User = Depends(get_current_active_superuser)
):
    zarpe = Zarpe.model_validate(zarpe_in, update={"id_usuario_created": current_user.id})
    session.add(zarpe)
    session.commit()
    session.refresh(zarpe)
    return zarpe


@router.put('/zarpe/{id}', response_model=Zarpe)
async def update_zarpe(
        id: int,
        zarpe_in: ZarpeUpdate,
        session: SessionDep,
        current_user: User = Depends(get_current_active_superuser)
):
    zarpe_db = session.get(Zarpe, id)
    if not zarpe_db:
        raise HTTPException(status_code=404, detail="No se encontro Zarpe")
    zarpe_data = zarpe_in.model_dump(exclude_unset=True)
    zarpe_db.sqlmodel_update(
        zarpe_data,
        update={
            "id_usuario_updated": current_user.id,
            "updated_date": datetime.datetime.now()
        }
    )
    session.add(zarpe_db)
    session.commit()
    session.refresh(zarpe_db)
    return zarpe_db


@router.delete('/zarpe/{id}')
async def delete_zarpe(
        id: int,
        session: SessionDep
):
    zarpe = session.get(Zarpe, id)
    if not zarpe:
        raise HTTPException(status_code=404, detail="No se encontro")
    session.delete(zarpe)
    session.commit()
    return JSONResponse(status_code=200, content={"mensaje": "Eliminado con exito", "Zarpe": jsonable_encoder(zarpe)})
