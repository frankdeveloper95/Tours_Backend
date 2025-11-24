import datetime
import random
from random import randint

from faker import Faker
from sqlmodel import Session, select

from app.core.database import engine
from app.models import Tour, Operadora, Guia


def create_tour():
    fake = Faker()
    with Session(engine) as session:
        operadoras = session.exec(select(Operadora.id).limit(3)).all()
        guias = session.exec(select(Guia.id).limit(3)).all()
        nombres = ["Isla de la Plata", "Machalilla", "Frailes"]
        horas_inicio = [
            datetime.time.fromisoformat("08:00:00"),
            datetime.time.fromisoformat("10:00:00"),
            datetime.time.fromisoformat("14:00:00")
        ]
        horas_fin = [
            datetime.time.fromisoformat("10:00:00"),
            datetime.time.fromisoformat("12:00:00"),
            datetime.time.fromisoformat("16:00:00")
        ]
        for i, (operadora, guia, nombre, hora_i, hora_f) in enumerate(zip(operadoras, guias, nombres, horas_inicio, horas_fin)):
            fecha = datetime.datetime.now() + datetime.timedelta(days=7)
            tour = Tour(
                id_operadora=operadora,
                id_guia=guia,
                nombre=nombre,
                descripcion=fake.text(max_nb_chars=60),
                fecha=datetime.date(year=fecha.year, month=fecha.month, day=fecha.day),
                hora_inicio=hora_i,
                hora_fin=hora_f,
                precio=random.randint(10, 30),
                capacidad_maxima=random.randint(10, 15),
                destino=nombre,
                image_url=None
            )
            session.add(tour)
            session.flush()
            tour.image_url = f"/images/tours/{tour.id}"
            session.commit()
        session.close()


def main():
    create_tour()


if __name__ == "__main__":
    main()
