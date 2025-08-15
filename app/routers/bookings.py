# app/routers/bookings.py

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from datetime import datetime
from .. import schemas, models
from ..database import get_db

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)

# Endpoint to get seating availability by movie and room
@router.get(
    "/movies/{movie_id}/rooms/{room_id}/seats",
    summary="Get seating availability for a movie in a room",
    description="Retrieve the seating layout for a specific movie within a room, showing which seats are available or booked. Returns a 404 error if the movie, room, or schedule is not found."
)
def get_available_seats_by_movie_and_room(
    movie_id: int = Path(..., description="The unique ID of the movie."),
    room_id: int = Path(..., description="The unique ID of the room."),
    db: Session = Depends(get_db)
):
    # Find the schedule for the given movie and room
    schedule = db.query(models.Schedule).filter(
        models.Schedule.movie_id == movie_id,
        models.Schedule.room_id == room_id
    ).first()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found for this movie and room combination"
        )
    
    # Use the schedule to find the room details
    room = db.query(models.Room).filter(models.Room.id == schedule.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Get booked seats
    booked_seats = db.query(models.Booking.row, models.Booking.seat).filter(
        models.Booking.schedule_id == schedule.id
    ).all()

    booked_seats_set = set((row, seat) for row, seat in booked_seats)

    # Build the seating layout
    seating_layout = []
    for row in range(1, room.rows + 1):
        row_seats = []
        for seat in range(1, room.seats_per_row + 1):
            is_booked = (row, seat) in booked_seats_set
            row_seats.append({
                "row": row,
                "seat": seat,
                "is_booked": is_booked
            })
        seating_layout.append(row_seats)

    return {
        "room_name": room.name,
        "total_rows": room.rows,
        "seats_per_row": room.seats_per_row,
        "seating_layout": seating_layout
    }

# Endpoint to get the seating layout and availability for a specific schedule
@router.get(
    "/{schedule_id}/seats",
    summary="Get seating availability",
    description="Retrieve the seating layout for a given schedule, showing which seats are available or booked. This endpoint provides a detailed map of the room, including row and seat numbers, and their current booking status."
)
def get_available_seats(
    schedule_id: int = Path(..., description="The unique ID of the schedule to check."),
    db: Session = Depends(get_db)
):
    schedule = db.query(models.Schedule).filter(models.Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    room = db.query(models.Room).filter(models.Room.id == schedule.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    booked_seats = db.query(models.Booking.row, models.Booking.seat).filter(
        models.Booking.schedule_id == schedule_id
    ).all()

    booked_seats_set = set((row, seat) for row, seat in booked_seats)

    seating_layout = []
    for row in range(1, room.rows + 1):
        row_seats = []
        for seat in range(1, room.seats_per_row + 1):
            is_booked = (row, seat) in booked_seats_set
            row_seats.append({
                "row": row,
                "seat": seat,
                "is_booked": is_booked
            })
        seating_layout.append(row_seats)

    return {
        "room_name": room.name,
        "total_rows": room.rows,
        "seats_per_row": room.seats_per_row,
        "seating_layout": seating_layout
    }

# Endpoint to create a new booking
@router.post(
    "/",
    response_model=schemas.Booking,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new booking",
    description="Books a specific seat for a movie schedule. Validates that the seat is available, exists within the room's dimensions, and that the schedule is valid."
)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    schedule = db.query(models.Schedule).filter(models.Schedule.id == booking.schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    room = db.query(models.Room).filter(models.Room.id == schedule.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Check if the seat is valid for the room
    if not (1 <= booking.row <= room.rows and 1 <= booking.seat <= room.seats_per_row):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid seat for this room")

    # Check if the seat is already booked
    existing_booking = db.query(models.Booking).filter(
        models.Booking.schedule_id == booking.schedule_id,
        models.Booking.row == booking.row,
        models.Booking.seat == booking.seat
    ).first()

    if existing_booking:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Seat is already booked")

    db_booking = models.Booking(**booking.model_dump(), timestamp=datetime.now())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking