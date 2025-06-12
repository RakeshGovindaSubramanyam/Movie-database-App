from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    year = Column(Integer)
    genre = Column(String)
    director = Column(String)
    actors = Column(String)
    plot = Column(String)
    poster = Column(String)
    rating = Column(Float)
