from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.settings import settings

engine = create_engine(str(settings.DB_DSN), execution_options={"isolation_level": "AUTOCOMMIT", "pool_pre_ping": True})
session = sessionmaker(bind=engine)


def dbsession() -> Session:
    global session
    local_session = session()

    return local_session
