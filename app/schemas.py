# app/schemas.py

from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from datetime import datetime, date, time
from typing import List

# Base Schemas
class RoomBase(BaseModel):
    name: str = Field(..., example="Screen 1")
    rows: int = Field(..., gt=0, example=10)
    seats_per_row: int = Field(..., gt=0, example=15)

class MovieBase(BaseModel):
    title: str = Field(..., example="The Matrix")
    poster: str = Field(..., example="https://example.com/matrix.jpg")

class ScheduleBase(BaseModel):
    show_date: date = Field(..., example="2025-08-15")
    start_time: time = Field(..., example="18:00")

    @field_serializer('start_time')
    def serialize_start_time(self, start_time: time) -> str:
        return start_time.strftime('%H:%M')

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
    room_id: int = Field(..., example=1)

class ScheduleCreateInRoom(ScheduleBase):
    movie_id: int = Field(..., example=1)

class BookingCreate(BookingBase):
    schedule_id: int = Field(..., example=1)

# Schemas for Reading objects (responses)
class Movie(MovieBase):
    id: int = Field(..., example=1)
    
    model_config = ConfigDict(from_attributes=True)

class Schedule(ScheduleBase):
    id: int = Field(..., example=1)
    room_id: int = Field(..., example=1)
    movie: Movie
    
    model_config = ConfigDict(from_attributes=True)

class Room(RoomBase):
    id: int = Field(..., example=1)
    schedules: List[Schedule] = []
    
    model_config = ConfigDict(from_attributes=True)

class Booking(BookingBase):
    id: int = Field(..., example=1)
    schedule_id: int = Field(..., example=1)
    timestamp: datetime = Field(..., example="2025-08-15T10:30:00")
    
    model_config = ConfigDict(from_attributes=True)