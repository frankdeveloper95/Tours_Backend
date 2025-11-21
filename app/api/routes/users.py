import uuid
from typing import Annotated

from fastapi import APIRouter, Query, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.params import Depends
from sqlmodel import select

from app.api.deps import SessionDep, get_current_active_superuser
from app.core.security import get_password_hash
from app.models import User, UserCreate, UserUpdate

router = APIRouter(tags=["users"], dependencies=[Depends(get_current_active_superuser)])


@router.post("/users", response_model=User)
async def add_user(user: UserCreate, session: SessionDep):
    db_user = User.model_validate(user, update={"hashed_password": get_password_hash(user.password)})
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.get("/users", response_model=list[User])
async def get_users(session: SessionDep, offset: int = 0,limit: Annotated[int, Query(le=100)] = 100):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@router.get("/users/{user_id}", response_model=User)
async def get_user_by_id(user_id: uuid.UUID, session: SessionDep):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    return user_db

@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id:uuid.UUID, user: UserUpdate, session: SessionDep):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    if user.email is not None and user.email != user_db.email:
        existing_user = session.exec(select(User).where(User.email == user.email, User.id != user_id)).first()
        if existing_user:
            raise HTTPException(status_code=409, detail="Este correo ya está en uso")
    user_data = user.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db

@router.delete("/users/{user_id}")
async def delete_user(user_id: uuid.UUID, session: SessionDep):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user_db)
    session.commit()
    return JSONResponse(content={"message":"Usuario Eliminado","user":jsonable_encoder(user_db)})

