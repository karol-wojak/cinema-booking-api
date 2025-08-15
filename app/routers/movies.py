# app/routers/movies.py

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import get_db

router = APIRouter(
    prefix="/movies",
    tags=["movies"],
)

# Endpoint to get a list of all movies
@router.get(
    "/movies/",
    response_model=list[schemas.Movie],
    summary="Get all movies",
    description="Retrieve a list of all movies in the database, including their details and poster URLs."
)
def get_all_movies(db: Session = Depends(get_db)):
    movies = db.query(models.Movie).all()
    return movies

# Endpoint to get a single movie by ID
@router.get(
    "/movies/{movie_id}",
    response_model=schemas.Movie,
    summary="Get a single movie",
    description="Retrieve a single movie by its unique ID. Returns a 404 error if the movie is not found."
)
def get_movie(
    movie_id: int = Path(..., description="The unique ID of the movie to retrieve."),
    db: Session = Depends(get_db)
):
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
    description="Creates a new movie with a unique title and a poster URL. A conflict error is returned if a movie with the same title already exists."
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
    description="Updates an existing movie's details. An update is only permitted if the movie has no existing schedules."
)
def update_movie(
    movie: schemas.MovieCreate,
    movie_id: int = Path(..., description="The unique ID of the movie to update."),
    db: Session = Depends(get_db)
):
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
    description="Deletes a movie by its ID. This operation is only permitted if the movie has no existing schedules to prevent data integrity issues."
)
def delete_movie(
    movie_id: int = Path(..., description="The unique ID of the movie to delete."),
    db: Session = Depends(get_db)
):
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