from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    rows = Column(Integer)
    seats_per_row = Column(Integer)

    schedules = relationship("Schedule", back_populates="room")

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    poster = Column(String)  # Stores the URL for the movie poster

    schedules = relationship("Schedule", back_populates="movie")

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime)

    room_id = Column(Integer, ForeignKey("rooms.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))

    room = relationship("Room", back_populates="schedules")
    movie = relationship("Movie", back_populates="schedules")
    bookings = relationship("Booking", back_populates="schedule")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    row = Column(Integer)
    seat = Column(Integer)
    timestamp = Column(DateTime)

    schedule_id = Column(Integer, ForeignKey("schedules.id"))

    schedule = relationship("Schedule", back_populates="bookings")