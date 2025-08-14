from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import get_db

router = APIRouter(
    prefix="/rooms",
    tags=["rooms"],
)

# Endpoint to get a list of all rooms
@router.get("/", response_model=list[schemas.Room])
def get_all_rooms(db: Session = Depends(get_db)):
    rooms = db.query(models.Room).all()
    return rooms

# Endpoint to create a new room
@router.post("/", response_model=schemas.Room, status_code=status.HTTP_201_CREATED)
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    # Check if a room with the same name already exists
    existing_room = db.query(models.Room).filter(models.Room.name == room.name).first()
    if existing_room:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A room with this name already exists"
        )

    db_room = models.Room(**room.model_dump())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

# Endpoint to create a new movie
@router.post("/movies/", response_model=schemas.Movie, status_code=status.HTTP_201_CREATED)
def create_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    db_movie = models.Movie(**movie.model_dump())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

# Endpoint to create a new schedule for a room and movie
@router.post("/{room_id}/schedules/", response_model=schemas.Schedule, status_code=status.HTTP_201_CREATED)
def create_schedule_for_room(room_id: int, schedule: schemas.ScheduleCreate, db: Session = Depends(get_db)):
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
    
    # Check if a schedule with the same movie and start time already exists in this room
    existing_schedule = db.query(models.Schedule).filter(
        models.Schedule.room_id == room_id,
        models.Schedule.movie_id == schedule.movie_id,
        models.Schedule.start_time == schedule.start_time
    ).first()
    if existing_schedule:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This movie is already scheduled for this room at the specified time"
        )

    db_schedule = models.Schedule(**schedule.model_dump(), room_id=room_id)
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

# Endpoint to get a list of all schedules
@router.get("/{room_id}/schedules/", response_model=list[schemas.Schedule])
def get_schedules_for_room(room_id: int, db: Session = Depends(get_db)):
    schedules = db.query(models.Schedule).filter(models.Schedule.room_id == room_id).all()
    return schedules