# app/database/base.py

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def init_db():
    from app.database.session import engine
    from app.database.models import attraction
    Base.metadata.create_all(bind=engine)