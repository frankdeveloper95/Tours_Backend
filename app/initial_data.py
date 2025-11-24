import logging

from sqlmodel import Session

from app.core.database import engine, init_db
from app.seeders.guia import create_guias
from app.seeders.operadora import create_operadoras
from app.seeders.users import create_user
from app.seeders.tour import create_tour
from app.seeders.reserva import create_reservas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    logger.info("Creating initial data")
    init()
    create_user()
    create_operadoras()
    create_guias()
    create_tour()
    create_reservas()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
