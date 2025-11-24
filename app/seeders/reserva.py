import datetime
import random

from sqlmodel import Session, select

from app.core.database import engine
from app.models import Reservas, User, Estado_Reserva, ReservaEnum


def create_reservas():
    with Session(engine) as session:
        usuarios = session.exec(select(User).limit(3)).all()
        pagada = Estado_Reserva(estado=ReservaEnum.PAGADA)
        pendiente = Estado_Reserva(estado=ReservaEnum.PENDIENTE)
        cancelada = Estado_Reserva(estado=ReservaEnum.CANCELADA)
        session.add(pagada)
        session.add(pendiente)
        session.add(cancelada)
        session.commit()
        for i, user in enumerate(usuarios):
            reserva = Reservas(
                id_tour = i + 1,
                id_usuario = user.id,
                nombre_cliente = user.nombre + " " + user.apellido,
                email_cliente = user.email,
                numero_personas = random.randint(1, 5),
                fecha_reserva = datetime.datetime.now()
            )
            session.add(reserva)
            session.commit()
        session.close()


def main():
    create_reservas()


if __name__ == "__main__":
    main()
