import re

import sqlalchemy
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.settings import Settings


settings = Settings()

@as_declarative()
class Base:
    """Base class for all database entities"""

    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate database table name automatically.
        Convert CamelCase class name to snake_case db table name.
        """
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()

    def __repr__(self) -> str:
        attrs = []
        for c in self.__table__.columns:
            attrs.append(f"{c.name}={getattr(self, c.name)}")
        return "{}({})".format(self.__class__.__name__, ', '.join(attrs))


class VkUser(Base):
    vk_id: Mapped[int] = mapped_column(sqlalchemy.BIGINT, primary_key=True)
    surname: Mapped[int] = mapped_column(sqlalchemy.String, nullable=False)
    number: Mapped[int] = mapped_column(sqlalchemy.String, nullable=False)


engine = create_engine(url=str(settings.DB_DSN), pool_pre_ping=True, isolation_level="AUTOCOMMIT")
Session = sessionmaker(bind=engine)
session = Session()


def reconnect_session():
    global engine
    global Session
    global session

    session.rollback()
    engine = create_engine(url=str(settings.DB_DSN), pool_pre_ping=True, isolation_level="AUTOCOMMIT")
    Session = sessionmaker(bind=engine)
    session = Session()
    session.rollback()
