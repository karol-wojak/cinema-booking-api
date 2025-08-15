from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

# Base Schemas
class RoomBase(BaseModel):
    name: str = Field(..., example="Room 1")
    rows: int = Field(..., gt=0, example=10)
    seats_per_row: int = Field(..., gt=0, example=15)

class MovieBase(BaseModel):
    title: str = Field(..., example="The Matrix")
    poster: str = Field(..., example="https://example.com/matrix.jpg")

class ScheduleBase(BaseModel):
    start_time: datetime = Field(..., example="2025-08-15T10:00:00")

class BookingBase(BaseModel):
    row: int = Field(..., example=5)
    seat: int = Field(..., example=5)

# Schemas for Creating objects (requests)
class RoomCreate(RoomBase):
    pass

class MovieCreate(MovieBase):
    pass

class ScheduleCreate(ScheduleBase):
    movie_id: int = Field(..., example=1)

class BookingCreate(BookingBase):
    schedule_id: int = Field(..., example=1)

# Schemas for Reading objects (responses)
class Room(RoomBase):
    id: int = Field(..., example=1)

    class Config:
        from_attributes = True

class Movie(MovieBase):
    id: int = Field(..., example=1)

    class Config:
        from_attributes = True

class Booking(BookingBase):
    id: int = Field(..., example=1)
    schedule_id: int = Field(..., example=1)
    timestamp: datetime = Field(..., example="2025-08-15T10:30:00")
    
    class Config:
        from_attributes = True

class Schedule(ScheduleBase):
    id: int = Field(..., example=1)
    room_id: int = Field(..., example=1)
    movie_id: int = Field(..., example=1)
    
    class Config:
        from_attributes = True
        