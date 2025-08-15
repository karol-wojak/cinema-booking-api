# app/routers/schedules.py

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session, joinedload
from .. import schemas, models
from ..database import get_db

router = APIRouter(
    prefix="/schedules",
    tags=["schedules"],
)

# Endpoint to create a new schedule for a room
@router.post(
    "/rooms/{room_id}",
    response_model=schemas.Schedule,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new schedule for a room",
    description="Creates a new movie schedule for a specific room. The room ID is taken from the URL, while the movie ID, date, and time are provided in the request body."
)
def create_schedule_for_room(
    schedule: schemas.ScheduleCreateInRoom,
    room_id: int = Path(..., description="The unique ID of the room for which the schedule will be created."),
    db: Session = Depends(get_db)
):
    # Check if the room exists
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    # Check if the movie exists
    movie = db.query(models.Movie).filter(models.Movie.id == schedule.movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    # Check for schedule conflicts
    existing_schedule = db.query(models.Schedule).filter(
        models.Schedule.room_id == room_id,
        models.Schedule.show_date == schedule.show_date,
        models.Schedule.start_time == schedule.start_time
    ).first()
    if existing_schedule:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A schedule for this room, date, and time already exists."
        )

    # Manually create the Schedule object to ensure the correct Python time object is used
    db_schedule = models.Schedule(
        room_id=room_id,
        movie_id=schedule.movie_id,
        show_date=schedule.show_date,
        start_time=schedule.start_time
    )
    
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

# Endpoint to get a list of all schedules for a specific room
@router.get(
    "/rooms/{room_id}",
    response_model=list[schemas.Schedule],
    summary="Get schedules for a room",
    description="Retrieve a list of all schedules for a given room. Returns a 404 error if the room does not exist, or an empty list if the room has no schedules."
)
def get_schedules_for_room(
    room_id: int = Path(..., description="The unique ID of the room to retrieve schedules for."),
    db: Session = Depends(get_db)
):
    # First, check if the room exists
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Then, retrieve schedules with an optimized query to fetch movie data
    schedules = db.query(models.Schedule).options(joinedload(models.Schedule.movie)).filter(
        models.Schedule.room_id == room_id
    ).all()
    
    return schedules