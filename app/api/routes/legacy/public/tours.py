
# LEGACY ROUTER - NO USAR (se reemplazó por app/api/routes/*_public.py)
import glob
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import select
from app.auth.deps import SessionDep
from app.models import Tour, TourPublic

router = APIRouter(tags=["public_tours"])


@router.get("/tours", response_model=list[TourPublic])
async def get_public_tours(session: SessionDep):
    tours = session.exec(select(Tour)).all()
    return tours

@router.get("/tours/{id}", response_model=TourPublic)
async def get_tour_by_id(
        id: int,
        session: SessionDep,
):
    tour = session.get(Tour, id)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour no encontrado")
    return tour

@router.get("/images/tours/{id}")
async def get_image_tour(
        id: int,
):
    file_path = 'C:/Users/Roberto/Dropbox/Mi PC (LAPTOP-FVSL94QG)/Documents/PROYECTO/Tours_Backend/app/assets/images/tours/'
    pattern = os.path.join(file_path, f"{id}.*")
    matches = glob.glob(pattern)
    if not matches:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    image_path = matches[0]
    return FileResponse(image_path)
