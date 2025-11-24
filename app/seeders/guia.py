import random

from faker import Faker
from sqlmodel import Session, select

from app.core.database import engine
from app.models import User, Guia, Operadora


def create_guias():
    fake = Faker()
    with Session(engine) as session:
        users = session.exec(select(User.id).offset(3).limit(5)).all()
        for user in users:
            guia = Guia(
                id_usuario=user,
                id_operadora=random.choice(session.exec(select(Operadora.id)).all()),
                calificacion=fake.random_int(min=1, max=5),
                idiomas=[fake.language_name(), fake.language_name(), fake.language_name()]
            )
            session.add(guia)
            session.commit()
        session.close()


def main():
    create_guias()


if __name__ == '__main__':
    main()
