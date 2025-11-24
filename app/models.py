import datetime
import uuid
from enum import StrEnum
from typing import Optional

from pydantic import EmailStr, BaseModel
from sqlmodel import Field, SQLModel, Column, Enum, Relationship, JSON


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

    operadora_created_user: Optional["Operadora"] = Relationship(
        back_populates="users_operadora_created",
        sa_relationship_kwargs={"foreign_keys": "Operadora.id_usuario_created"}
    )
    operadora_updated_user: Optional["Operadora"] = Relationship(
        back_populates="users_operadora_updated",
        sa_relationship_kwargs={"foreign_keys": "Operadora.id_usuario_updated"}
    )
    guia_usuario_id: Optional["Guia"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"foreign_keys": "Guia.id_usuario"}
    )
    guia_usuario_created: Optional["Guia"] = Relationship(
        back_populates="usuario_created",
        sa_relationship_kwargs={"foreign_keys": "Guia.id_usuario_created"}
    )
    guia_usuario_updated: Optional["Guia"] = Relationship(
        back_populates="usuario_updated",
        sa_relationship_kwargs={"foreign_keys": "Guia.id_usuario_updated"}
    )


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


class Operadora(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    razon_social: str = Field(max_length=150)
    correo: EmailStr = Field(unique=True, max_length=100)
    telefono: str = Field(unique=True, max_length=10)
    direccion: str = Field(max_length=100)
    created_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_date: datetime.datetime | None = None
    id_usuario_created: uuid.UUID | None = Field(foreign_key="user.id")
    id_usuario_updated: uuid.UUID | None = Field(default=None, foreign_key="user.id")

    users_operadora_created: User = Relationship(
        back_populates="operadora_created_user",
        sa_relationship_kwargs={"foreign_keys": "Operadora.id_usuario_created"}
    )
    users_operadora_updated: User = Relationship(
        back_populates="operadora_updated_user",
        sa_relationship_kwargs={"foreign_keys": "Operadora.id_usuario_updated"}
    )


class OperadoraCreate(SQLModel):
    nombre: str
    razon_social: str
    correo: EmailStr
    telefono: str
    direccion: str


class OperadoraUpdate(SQLModel):
    nombre: str | None = None
    razon_social: str | None = None
    correo: EmailStr | None = None
    telefono: str | None = None
    direccion: str | None = None


class OperadoraOut(OperadoraCreate):
    id: int
    created_date: datetime.datetime
    updated_date: datetime.datetime | None
    id_usuario_created: uuid.UUID | None
    id_usuario_updated: uuid.UUID | None


class Guia(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_usuario: uuid.UUID | None = Field(unique=True, default=None, foreign_key="user.id")
    id_operadora: int | None = Field(default=None, foreign_key="operadora.id")
    calificacion: float | None = None
    idiomas: list[str] | None = Field(default=None, sa_column=Column(JSON))
    created_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_date: datetime.datetime | None = None
    id_usuario_created: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    id_usuario_updated: uuid.UUID | None = Field(default=None, foreign_key="user.id")

    usuario: User | None = Relationship(
        back_populates="guia_usuario_id",
        sa_relationship_kwargs={"foreign_keys": "Guia.id_usuario"}
    )
    usuario_created: User | None = Relationship(
        back_populates="guia_usuario_created",
        sa_relationship_kwargs={"foreign_keys": "Guia.id_usuario_created"}
    )
    usuario_updated: User | None = Relationship(
        back_populates="guia_usuario_updated",
        sa_relationship_kwargs={"foreign_keys": "Guia.id_usuario_updated"}
    )


class GuiaCreate(SQLModel):
    id_usuario: uuid.UUID | None
    id_operadora: int | None = None
    calificacion: float | None = None
    idiomas: list[str]


class GuiaWithUser(SQLModel):
    id: int
    id_usuario: uuid.UUID | None
    usuario: UserPublic
    id_operadora: int | None
    calificacion: float | None
    idiomas: list[str] | None
    created_date: datetime.datetime
    updated_date: datetime.datetime | None
    id_usuario_created: uuid.UUID | None
    id_usuario_updated: uuid.UUID | None


class GuiaUpdate(SQLModel):
    id_operadora: int | None = None
    calificacion: float | None = None
    idiomas: list[str] | None = None


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
