from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from .. import schemas, models
from ..database import get_db

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)

# Endpoint to get the seating layout and availability for a specific schedule
@router.get(
    "/{schedule_id}/seats",
    summary="Get seating availability",
    description="Retrieve the seating layout for a given schedule, showing which seats are available or booked."
)
def get_available_seats(schedule_id: int, db: Session = Depends(get_db)):
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
    description="Books a specific seat for a movie schedule. Validates that the seat is available and exists within the room's dimensions."
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