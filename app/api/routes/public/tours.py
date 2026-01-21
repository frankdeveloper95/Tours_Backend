
# LEGACY ROUTER - NO USAR (se reemplazó por app/api/routes/*_public.py)
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import select

from app.auth.deps import SessionDep
from app.models import Tour, TourPublic

router = APIRouter(tags=["public_tours"])

ASSETS_TOURS_DIR = Path(__file__).resolve().parents[3] / 'assets' / 'images' / 'tours'

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
async def get_image_tour(id: int):
    file_dir = ASSETS_TOURS_DIR
    if not file_dir.exists():
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    matches = list(file_dir.glob(f"{id}.*"))
    if not matches:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return FileResponse(matches[0])