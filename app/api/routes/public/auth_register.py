# app/api/routes/public/auth_register.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy import or_

from app.models import User, UserCreate, UserPublic
from app.auth.deps import get_session
from app.core.security import get_password_hash

router = APIRouter(tags=["auth_register"], prefix="/auth_register")


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, session: Session = Depends(get_session)):
    # 1) Verificar duplicados SOLO si vienen con valor (evita falsos positivos por NULL)
    filters = []

    email = (user_in.email or "").strip()
    cedula = (user_in.cedula or "").strip()

    if email:
        filters.append(User.email == email)

    if cedula:
        filters.append(User.cedula == cedula)

    if filters:
        existing_user = session.exec(select(User).where(or_(*filters))).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email o la cédula ya están registrados.",
            )

    # 2) Crear usuario nuevo (rol/estado AUTOMÁTICOS)
    db_user = User(
        email=email,
        nombre=user_in.nombre,
        apellido=user_in.apellido,
        telefono=user_in.telefono,
        cedula=cedula,
        hashed_password=get_password_hash(user_in.password),
        rol_id=2,    # usuario normal
        estado_id=1  # ACTIVO
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # 3) Devolver datos públicos (sin password) — INCLUYE rol_id (porque UserPublic lo requiere)
    return UserPublic(
        email=db_user.email,
        nombre=db_user.nombre,
        apellido=db_user.apellido,
        rol_id=db_user.rol_id,
        # estado_id=db_user.estado_id,  # descomenta SOLO si tu UserPublic también lo exige
    )
