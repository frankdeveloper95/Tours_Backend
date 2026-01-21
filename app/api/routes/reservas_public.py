from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import selectinload
from sqlalchemy import text
from sqlmodel import select

from app.auth.deps import SessionDep, get_current_active_user
from app.models import (
    Reservas,
    ReservasCreatePublic,
    Estado_Reserva,
    ReservaEnum,
    User
)
from app.reservas.repository import ReservasRepository
from app.reservas.service import ReservasService

router = APIRouter(prefix="/reservas", tags=["Reservas Públicas"])


# ============================================================
# 1) Crear reserva pública (sin pago)
# ============================================================
@router.post("/crear")
def crear_reserva_publica(
    reserva_in: ReservasCreatePublic,
    session: SessionDep,
    current_user: User = Depends(get_current_active_user),
):
    return ReservasService.create_reserva(session, reserva_in, current_user)


# ============================================================
# 2) Obtener todas las reservas del usuario autenticado
# ============================================================
@router.get("/mis-reservas")
def get_mis_reservas(
    session: SessionDep,
    current_user: User = Depends(get_current_active_user),
):
    reservas = ReservasRepository.get_by_user(session, current_user.id)
    return {"reservas": reservas}


# ============================================================
# 2.1) Obtener reservas con TOTAL calculado (SQL directo)
# ============================================================
@router.get("/mis-reservas-totales")
def get_mis_reservas_totales(
    session: SessionDep,
    current_user: User = Depends(get_current_active_user),
):
    query = text("""
        SELECT
            r.id,
            r.nombre_cliente,
            r.numero_personas,
            r.fecha_reserva,
            r.id_tour,

            t.nombre AS tour_nombre,
            t.precio AS tour_precio,
            t.image_url AS tour_imagen,
            t.destino AS tour_destino,
            t.hora_inicio AS tour_hora_inicio,
            t.hora_fin AS tour_hora_fin,

            (r.numero_personas * t.precio) AS total

        FROM reservas r
        JOIN tour t ON r.id_tour = t.id
        WHERE r.id_usuario = CAST(:user_id AS uuid)
        ORDER BY r.created_date DESC
    """)

    result = session.exec(
        query,
        params={"user_id": str(current_user.id)}
    ).all()

    reservas = [
        {
            "id": row.id,
            "nombre_cliente": row.nombre_cliente,
            "numero_personas": row.numero_personas,
            "fecha_reserva": row.fecha_reserva,
            "id_tour": row.id_tour,

            "tour": {
                "nombre": row.tour_nombre,
                "precio": row.tour_precio,
                "imagen": row.tour_imagen,
                "destino": row.tour_destino,
                "hora_inicio": row.tour_hora_inicio,
                "hora_fin": row.tour_hora_fin,
            },

            "total": row.total,
        }
        for row in result
    ]

    return {"reservas": reservas}

# ============================================================
# 3) Obtener una reserva específica del usuario
# ============================================================
@router.get("/{reserva_id}")
def get_reserva_by_id(
    reserva_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_active_user),
):
    reserva = ReservasRepository.get_by_id(session, reserva_id)

    if reserva.id_usuario != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    return {"reserva": reserva}


# ============================================================
# 4) Obtener reservas por estado (PAGADA, PENDIENTE, CANCELADA)
# ============================================================
@router.get("/estado/{estado}")
def get_reservas_por_estado(
    estado: ReservaEnum,
    session: SessionDep,
    current_user: User = Depends(get_current_active_user),
):
    reservas = session.exec(
        select(Reservas)
        .where(Reservas.id_usuario == current_user.id)
        .where(Reservas.estado.has(Estado_Reserva.estado == estado))
        .options(
            selectinload(Reservas.tour),
            selectinload(Reservas.estado)
        )
    ).all()

    return {"reservas": reservas}
