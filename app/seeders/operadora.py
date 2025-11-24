from faker import Faker
from sqlmodel import Session

from app.core.database import engine
from app.models import Operadora


def create_operadoras():
    fake = Faker()
    with Session(engine) as session:
        for _ in range(10):
            company=fake.company()
            operadora=Operadora(
                nombre=company,
                razon_social=company,
                correo=fake.company_email(),
                telefono=fake.unique.numerify("09########"),
                direccion= fake.address()
            )
            session.add(operadora)
            session.commit()
        session.close()

def main():
    create_operadoras()

if __name__ == '__main__':
    main()