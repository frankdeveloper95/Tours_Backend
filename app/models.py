import datetime
import uuid
from enum import StrEnum

from pydantic import EmailStr, BaseModel
from sqlmodel import Field, SQLModel, Column, Enum, Relationship


class RolEnum(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"
    GUEST = "GUEST"


class Rol(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    rol: RolEnum = Field(sa_column=Column(Enum(RolEnum)), default=RolEnum.GUEST)

    users: list["User"] = Relationship(back_populates="rol")


class EstadoEnum(StrEnum):
    ACTIVE = "ACTIVO"
    INACTIVE = "INACTIVO"


class Estado(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    estado: EstadoEnum = Field(sa_column=Column(Enum(EstadoEnum)), default=EstadoEnum.ACTIVE)
    users: list["User"] = Relationship(back_populates="estado")


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    rol_id: int | None = Field(foreign_key="rol.id")
    estado_id: int | None = Field(foreign_key="estado.id")
    cedula: str = Field(unique=True, index=True, max_length=10)
    nombre: str = Field(default=None, max_length=255)
    apellido: str = Field(default=None, max_length=255)
    telefono: str | None = Field(default=None, max_length=10)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    hashed_password: str
    created_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_date: datetime.datetime | None = None

    rol: Rol = Relationship(back_populates="users")
    estado: Estado = Relationship(back_populates="users")


class UserCreate(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    nombre: str = Field(default=None, max_length=255)
    apellido: str = Field(default=None, max_length=255)
    password: str = Field(min_length=8, max_length=40)
    rol_id: int = Field(default=2)
    estado_id: int = Field(default=1)
    telefono: str | None = Field(default=None, max_length=10)
    cedula: str = Field(max_length=10)


class UserPublic(BaseModel):
    email: EmailStr
    rol_id: int
    nombre: str | None
    apellido: str | None


class UserUpdate(SQLModel):
    email: EmailStr | None = None
    nombre: str | None = None
    apellido: str | None = None
    telefono: str | None = None
    rol_id: int | None = None
    estado_id: int | None = None


# Contents of JWT token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


class TokenData(BaseModel):
    username: str | None = None


class Stripe(BaseModel):
    product_id: int | None = None
