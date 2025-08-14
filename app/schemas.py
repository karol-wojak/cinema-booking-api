from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

# Base Schemas
class RoomBase(BaseModel):
    name: str
    rows: int = Field(..., gt=0) # Ensures value is greater than 0
    seats_per_row: int = Field(..., gt=0) # Ensures value is greater than 0

class MovieBase(BaseModel):
    title: str
    poster: str

class ScheduleBase(BaseModel):
    start_time: datetime

class BookingBase(BaseModel):
    row: int
    seat: int

# Schemas for Creating objects (requests)
class RoomCreate(RoomBase):
    pass

class MovieCreate(MovieBase):
    pass

class ScheduleCreate(ScheduleBase):
    movie_id: int

class BookingCreate(BookingBase):
    schedule_id: int

# Schemas for Reading objects (responses)
class Room(RoomBase):
    id: int
    # schedules: List['Schedule'] = []

    class Config:
        from_attributes = True

class Movie(MovieBase):
    id: int

    class Config:
        from_attributes = True

class Booking(BookingBase):
    id: int
    schedule_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class Schedule(ScheduleBase):
    id: int
    room_id: int
    movie_id: int
    # room: Room
    # movie: Movie
    bookings: List['Booking'] = []

    class Config:
        from_attributes = True

# Call model_rebuild() after all related schemas are defined
# Room.model_rebuild()
# Schedule.model_rebuild()