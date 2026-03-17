# app/database/models/attraction.py

from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector
from app.database.base import Base

class Attraction(Base):
    __tablename__ = "attractions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    embedding = Column(Vector(3072))