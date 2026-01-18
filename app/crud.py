from sqlmodel import Session, select
from app.models import User, UserCreate
from app.core.security import get_password_hash, verify_password


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    # No existe el usuario
    if not db_user:
        return None
    # Usuario inactivo (estado_id = 2)
    if db_user.estado_id != 1:
        return None
    # Password incorrecto
    if not verify_password(password, db_user.hashed_password):
        return None
    # Usuario válido y activo
    return db_user

