from collections.abc import Iterator

from sqlmodel import Session, create_engine

from App.config import get_settings

setting = get_settings()

engine = create_engine(setting.database_url, echo=setting.sql_echo, pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
