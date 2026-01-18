from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session

from app import crud
from app.core.database import engine
from app.core.security import SECRET_KEY, ALGORITHM
from app.models import User, TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


# =========================
# Sesión DB
# =========================
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# =========================
# Usuario autenticado
# =========================
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = crud.get_user_by_email(session=session, email=username)
    if user is None:
        raise credentials_exception

    return user


# =========================
# Usuario activo (NORMAL)
# =========================
async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    # estado_id = 1 → ACTIVO
    if current_user.estado_id != 1:
        raise HTTPException(status_code=403, detail="El usuario está inactivo")
    return current_user


# =========================
# Usuario administrador
# =========================
async def get_current_active_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.estado_id != 1:
        raise HTTPException(status_code=403, detail="El usuario está inactivo")

    # rol_id = 1 → admin 
    if current_user.rol_id != 1:
        raise HTTPException(status_code=403, detail="No tienes los privilegios para realizar esta acción")

    return current_user
