from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import get_db

router = APIRouter(
    prefix="/rooms",
    tags=["rooms"],
)

# Endpoint to get a list of all rooms
@router.get(
    "/",
    response_model=list[schemas.Room],
    summary="Get all rooms",
    description="Retrieve a list of all cinema rooms and their details."
)
def get_all_rooms(db: Session = Depends(get_db)):
    rooms = db.query(models.Room).all()
    return rooms

# Endpoint to get a single room by ID
@router.get(
    "/{room_id}",
    response_model=schemas.Room,
    summary="Get a single room",
    description="Retrieve a single cinema room by its unique ID."
)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    return room

# Endpoint to create a new room
@router.post(
    "/",
    response_model=schemas.Room,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new room",
    description="Creates a new cinema room with a unique name and seating dimensions."
)
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

# Endpoint to update a room
@router.put(
    "/{room_id}",
    response_model=schemas.Room,
    summary="Update a room",
    description="Updates an existing room's details, such as name and seating capacity."
)
def update_room(room_id: int, room: schemas.RoomCreate, db: Session = Depends(get_db)):
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not db_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Check if the room has any schedules before updating
    schedules = db.query(models.Schedule).filter(models.Schedule.room_id == room_id).all()
    if schedules:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot update room, it has existing schedules"
        )
    
    for key, value in room.model_dump().items():
        setattr(db_room, key, value)
    db.commit()
    db.refresh(db_room)
    return db_room

# Endpoint to delete a room
@router.delete(
    "/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a room",
    description="Deletes a room by its ID, but only if it has no existing schedules."
)
def delete_room(room_id: int, db: Session = Depends(get_db)):
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not db_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Check if the room has any schedules before deleting
    schedules = db.query(models.Schedule).filter(models.Schedule.room_id == room_id).all()
    if schedules:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete room, it has existing schedules"
        )

    db.delete(db_room)
    db.commit()
    return {"message": "Room deleted successfully"}

# Endpoint to get a list of all movies
@router.get(
    "/movies/",
    response_model=list[schemas.Movie],
    summary="Get all movies",
    description="Retrieve a list of all movies in the database."
)
def get_all_movies(db: Session = Depends(get_db)):
    movies = db.query(models.Movie).all()
    return movies

# Endpoint to get a single movie by ID
@router.get(
    "/movies/{movie_id}",
    response_model=schemas.Movie,
    summary="Get a single movie",
    description="Retrieve a single movie by its unique ID."
)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    return movie

# Endpoint to create a new movie
@router.post(
    "/movies/",
    response_model=schemas.Movie,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new movie",
    description="Creates a new movie with a unique title and a poster URL."
)
def create_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    # Check if a movie with the same title already exists
    existing_movie = db.query(models.Movie).filter(models.Movie.title == movie.title).first()
    if existing_movie:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A movie with this title already exists"
        )

    db_movie = models.Movie(**movie.model_dump())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

# Endpoint to update a movie
@router.put(
    "/movies/{movie_id}",
    response_model=schemas.Movie,
    summary="Update a movie",
    description="Updates an existing movie's details."
)
def update_movie(movie_id: int, movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not db_movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )

    # Check if the movie has any schedules before updating
    schedules = db.query(models.Schedule).filter(models.Schedule.movie_id == movie_id).all()
    if schedules:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot update movie, it has existing schedules"
        )

    for key, value in movie.model_dump().items():
        setattr(db_movie, key, value)
    db.commit()
    db.refresh(db_movie)
    return db_movie

# Endpoint to delete a movie
@router.delete(
    "/movies/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a movie",
    description="Deletes a movie by its ID, but only if it has no existing schedules."
)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not db_movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )

    # Check if the movie has any schedules before deleting
    schedules = db.query(models.Schedule).filter(models.Schedule.movie_id == movie_id).all()
    if schedules:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete movie, it has existing schedules"
        )

    db.delete(db_movie)
    db.commit()
    return {"message": "Movie deleted successfully"}

# Endpoint to create a new schedule for a room and movie
@router.post(
    "/{room_id}/schedules/",
    response_model=schemas.Schedule,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new schedule",
    description="Creates a new movie schedule for a specific room and time."
)
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
@router.get(
    "/{room_id}/schedules/",
    response_model=list[schemas.Schedule],
    summary="Get schedules for a room",
    description="Retrieve a list of all schedules for a given room."
)
def get_schedules_for_room(room_id: int, db: Session = Depends(get_db)):
    schedules = db.query(models.Schedule).filter(models.Schedule.room_id == room_id).all()
    return schedules