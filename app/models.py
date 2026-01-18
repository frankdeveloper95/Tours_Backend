import datetime as dt
import uuid
from enum import StrEnum
from typing import Optional, Dict, List

from pydantic import EmailStr, BaseModel
from sqlmodel import Field, SQLModel, Column, Enum, Relationship, JSON
from sqlalchemy.dialects.postgresql import JSONB

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
    created_date: dt.datetime = Field(default_factory=dt.datetime.now)
    updated_date: dt.datetime | None = None

    rol: "Rol" = Relationship(back_populates="users")
    estado: "Estado" = Relationship(back_populates="users")

    operadora_created_user: Optional["Operadora"] = Relationship(
        back_populates="users_operadora_created",
        sa_relationship_kwargs={"foreign_keys": "Operadora.id_usuario_created"},
    )
    operadora_updated_user: Optional["Operadora"] = Relationship(
        back_populates="users_operadora_updated",
        sa_relationship_kwargs={"foreign_keys": "Operadora.id_usuario_updated"},
    )

    guia_usuario_id: Optional["Guia"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"foreign_keys": "Guia.id_usuario"},
    )
    guia_usuario_created: Optional["Guia"] = Relationship(
        back_populates="usuario_created",
        sa_relationship_kwargs={"foreign_keys": "Guia.id_usuario_created"},
    )
    guia_usuario_updated: Optional["Guia"] = Relationship(
        back_populates="usuario_updated",
        sa_relationship_kwargs={"foreign_keys": "Guia.id_usuario_updated"},
    )

    tour_usuario_created: Optional["Tour"] = Relationship(
        back_populates="usuario_created",
        sa_relationship_kwargs={"foreign_keys": "Tour.id_usuario_created"},
    )
    tour_usuario_updated: Optional["Tour"] = Relationship(
        back_populates="usuario_updated",
        sa_relationship_kwargs={"foreign_keys": "Tour.id_usuario_updated"},
    )

    reservas_usuario_id: list["Reservas"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"foreign_keys": "Reservas.id_usuario"},
    )
    reservas_usuario_created: list["Reservas"] = Relationship(
        back_populates="usuario_created",
        sa_relationship_kwargs={"foreign_keys": "Reservas.id_usuario_created"},
    )
    reservas_usuario_updated: list["Reservas"] = Relationship(
        back_populates="usuario_updated",
        sa_relationship_kwargs={"foreign_keys": "Reservas.id_usuario_updated"},
    )

    zarpe_usuario_created: Optional["Zarpe"] = Relationship(
        back_populates="usuario_created",
        sa_relationship_kwargs={"foreign_keys": "Zarpe.id_usuario_created"},
    )
    zarpe_usuario_updated: Optional["Zarpe"] = Relationship(
        back_populates="usuario_updated",
        sa_relationship_kwargs={"foreign_keys": "Zarpe.id_usuario_updated"},
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
    created_date: dt.datetime = Field(default_factory=dt.datetime.now)
    updated_date: dt.datetime | None = None
    id_usuario_created: uuid.UUID | None = Field(foreign_key="user.id")
    id_usuario_updated: uuid.UUID | None = Field(default=None, foreign_key="user.id")

    users_operadora_created: "User" = Relationship(
        back_populates="operadora_created_user",
        sa_relationship_kwargs={"foreign_keys": "Operadora.id_usuario_created"},
    )
    users_operadora_updated: "User" = Relationship(
        back_populates="operadora_updated_user",
        sa_relationship_kwargs={"foreign_keys": "Operadora.id_usuario_updated"},
    )
    tours: list["Tour"] = Relationship(back_populates="operadora")


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
    created_date: dt.datetime
    updated_date: dt.datetime | None
    id_usuario_created: uuid.UUID | None
    id_usuario_updated: uuid.UUID | None


class Guia(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_usuario: uuid.UUID | None = Field(unique=True, default=None, foreign_key="user.id")
    id_operadora: int | None = Field(default=None, foreign_key="operadora.id")
    calificacion: float | None = None
    idiomas: list[str] | None = Field(default=None, sa_column=Column(JSON))
    created_date: dt.datetime = Field(default_factory=dt.datetime.now)
    updated_date: dt.datetime | None = None
    id_usuario_created: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    id_usuario_updated: uuid.UUID | None = Field(default=None, foreign_key="user.id")

    usuario: Optional["User"] = Relationship(
        back_populates="guia_usuario_id",
        sa_relationship_kwargs={"foreign_keys": "Guia.id_usuario"},
    )
    usuario_created: Optional["User"] = Relationship(
        back_populates="guia_usuario_created",
        sa_relationship_kwargs={"foreign_keys": "Guia.id_usuario_created"},
    )
    usuario_updated: Optional["User"] = Relationship(
        back_populates="guia_usuario_updated",
        sa_relationship_kwargs={"foreign_keys": "Guia.id_usuario_updated"},
    )
    tour_guia: list["Tour"] = Relationship(back_populates="guia")
    zarpes: list["Zarpe"] = Relationship(back_populates="guia")


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
    created_date: dt.datetime
    updated_date: dt.datetime | None
    id_usuario_created: uuid.UUID | None
    id_usuario_updated: uuid.UUID | None


class GuiaUpdate(SQLModel):
    id_operadora: int | None = None
    calificacion: float | None = None
    idiomas: list[str] | None = None


class Tour(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_operadora: int | None = Field(default=None, foreign_key="operadora.id")
    id_guia: int | None = Field(default=None, foreign_key="guia.id")

    nombre: str
    descripcion: str
    fecha: dt.date
    hora_inicio: dt.time
    hora_fin: dt.time
    precio: int
    capacidad_maxima: int
    destino: str

    image_url: str | None = Field(default=None)

    # NUEVOS CAMPOS
    incluye: List[str] = Field(default_factory=list, sa_column=Column(JSONB))
    no_incluye: List[str] = Field(default_factory=list, sa_column=Column(JSONB))
    que_llevar: List[str] = Field(default_factory=list, sa_column=Column(JSONB))
    itinerario: List[str] = Field(default_factory=list, sa_column=Column(JSONB))
    politicas: str | None = Field(default=None)

    created_date: dt.datetime = Field(default_factory=dt.datetime.now)
    updated_date: dt.datetime | None = Field(default=None)
    id_usuario_created: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    id_usuario_updated: uuid.UUID | None = Field(default=None, foreign_key="user.id")

    usuario_created: Optional["User"] = Relationship(
        back_populates="tour_usuario_created",
        sa_relationship_kwargs={"foreign_keys": "Tour.id_usuario_created"},
    )
    usuario_updated: Optional["User"] = Relationship(
        back_populates="tour_usuario_updated",
        sa_relationship_kwargs={"foreign_keys": "Tour.id_usuario_updated"},
    )

    operadora: Optional["Operadora"] = Relationship(back_populates="tours")
    guia: Optional["Guia"] = Relationship(back_populates="tour_guia")
    reservas: list["Reservas"] = Relationship(back_populates="tour")
    zarpes: list["Zarpe"] = Relationship(back_populates="tour")



class TourCreate(SQLModel):
    id_operadora: int
    id_guia: int
    nombre: str
    descripcion: str
    fecha: dt.date
    hora_inicio: dt.time
    hora_fin: dt.time
    precio: int
    capacidad_maxima: int
    destino: str
    image_url: str

    # NUEVOS CAMPOS
    incluye: List[str] = []
    no_incluye: List[str] = []
    que_llevar: List[str] = []
    itinerario: List[str] = []
    politicas: str | None = None

    id_usuario_created: uuid.UUID | None = None



class TourUpdate(SQLModel):
    id_operadora: int | None = None
    id_guia: int | None = None
    nombre: str | None = None
    descripcion: str | None = None
    fecha: dt.date | None = None
    hora_inicio: dt.time | None = None
    hora_fin: dt.time | None = None
    precio: int | None = None
    capacidad_maxima: int | None = None
    destino: str | None = None
    image_url: str | None = None

    #NUEVOS CAMPOS (opcionales para no pisar si no se envían)
    incluye: List[str] | None = None
    no_incluye: List[str] | None = None
    que_llevar: List[str] | None = None
    itinerario: List[str] | None = None
    politicas: str | None = None

    id_usuario_updated: uuid.UUID | None = None


class TourPublic(SQLModel):
    id: int
    nombre: str
    descripcion: str
    fecha: dt.date
    hora_inicio: dt.time
    hora_fin: dt.time
    precio: int
    capacidad_maxima: int
    destino: str
    operadora: Operadora
    guia: GuiaWithUser
    image_url: str

    # NUEVOS CAMPOS
    incluye: List[str] = []
    no_incluye: List[str] = []
    que_llevar: List[str] = []
    itinerario: List[str] = []
    politicas: str | None = None


class ReservaEnum(StrEnum):
    PAGADA = "PAGADA"
    PENDIENTE = "PENDIENTE"
    CANCELADA = "CANCELADA"


class Estado_Reserva(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    estado: ReservaEnum = Field(sa_column=Column(Enum(ReservaEnum)), default=ReservaEnum.PENDIENTE)

    reservas: list["Reservas"] = Relationship(back_populates="estado")


class Reservas(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_tour: int | None = Field(default=None, foreign_key="tour.id")
    id_usuario: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    id_reserva_estado: int = Field(default=1, foreign_key="estado_reserva.id")
    nombre_cliente: str = Field(max_length=255)
    email_cliente: str = Field(max_length=255)
    numero_personas: int
    fecha_reserva: dt.datetime | None = Field(default=None)
    fecha_modificacion_reserva: dt.datetime | None = Field(default=None)
    created_date: dt.datetime = Field(default_factory=dt.datetime.now)
    updated_date: dt.datetime | None = Field(default=None)
    id_usuario_created: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    id_usuario_updated: uuid.UUID | None = Field(default=None, foreign_key="user.id")

    # AQUÍ TAMBIÉN
    tour: Optional["Tour"] = Relationship(back_populates="reservas")
    estado: Optional["Estado_Reserva"] = Relationship(back_populates="reservas")

    usuario: Optional["User"] = Relationship(
        back_populates="reservas_usuario_id",
        sa_relationship_kwargs={"foreign_keys": "Reservas.id_usuario"},
    )
    usuario_created: Optional["User"] = Relationship(
        back_populates="reservas_usuario_created",
        sa_relationship_kwargs={"foreign_keys": "Reservas.id_usuario_created"},
    )
    usuario_updated: Optional["User"] = Relationship(
        back_populates="reservas_usuario_updated",
        sa_relationship_kwargs={"foreign_keys": "Reservas.id_usuario_updated"},
    )


class ReservasCreate(SQLModel):
    id_tour: int
    id_usuario: uuid.UUID
    id_reserva_estado: int = Field(default=2)
    nombre_cliente: str | None = Field(default=None, max_length=255)
    email_cliente: str | None = Field(default=None, max_length=255)
    numero_personas: int = Field(default=1)


class ParticipanteCreate(SQLModel):
    nombre: str = Field(max_length=255)
    email: Optional[str] = Field(default=None, max_length=255)


class ReservasCreatePublic(SQLModel):
    id_tour: int
    fecha_reserva: dt.datetime
    numero_personas: int = Field(default=1, ge=1)
    nombre_cliente: str = Field(max_length=255)
    email_cliente: EmailStr
    # participantes: List[ParticipanteCreate] = []  #


class ReservasCreateAdmin(ReservasCreatePublic):
    id_usuario: uuid.UUID
    id_reserva_estado: int = Field(default=2)


class ReservasUpdate(SQLModel):
    id_tour: int | None = None
    id_reserva_estado: int | None = None
    nombre_cliente: str | None = None
    email_cliente: str | None = None
    numero_personas: int | None = None


class ReservasPublic(SQLModel):
    tour: TourPublic
    estado: Estado_Reserva


class Zarpe(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_tour: int | None = Field(default=None, foreign_key="tour.id")
    id_guia: int | None = Field(default=None, foreign_key="guia.id")
    detalles: Dict = Field(sa_column=Column(JSON))
    capitan: str = Field(max_length=255)
    marinero: str = Field(max_length=255)
    observaciones: str = Field(max_length=255)
    id_usuario_created: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    id_usuario_updated: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    created_date: dt.datetime = Field(default_factory=dt.datetime.now)
    updated_date: dt.datetime | None = Field(default=None)

    # AQUÍ TAMBIÉN
    tour: Optional["Tour"] = Relationship(back_populates="zarpes")
    guia: Optional["Guia"] = Relationship(back_populates="zarpes")

    usuario_created: Optional["User"] = Relationship(
        back_populates="zarpe_usuario_created",
        sa_relationship_kwargs={"foreign_keys": "Zarpe.id_usuario_created"},
    )
    usuario_updated: Optional["User"] = Relationship(
        back_populates="zarpe_usuario_updated",
        sa_relationship_kwargs={"foreign_keys": "Zarpe.id_usuario_updated"},
    )


class ZarpeCreate(SQLModel):
    id_tour: int
    id_guia: int
    detalles: Dict
    capitan: str = Field(max_length=255)
    marinero: str = Field(max_length=255)
    observaciones: str = Field(max_length=255)


class ZarpeUpdate(SQLModel):
    id_tour: int | None = None
    id_guia: int | None = None
    detalles: Dict | None = None
    capitan: str | None = Field(default=None, max_length=255)
    marinero: str | None = Field(default=None, max_length=255)
    observaciones: str | None = Field(default=None, max_length=255)


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


class TokenData(BaseModel):
    username: str | None = None


class Stripe(BaseModel):
    product_id: int | None = None
