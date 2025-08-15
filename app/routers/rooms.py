from fastapi import APIRouter, Depends, HTTPException, status, Path
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
    description="Retrieve a list of all cinema rooms and their details. This endpoint provides a complete overview of all available rooms."
)
def get_all_rooms(db: Session = Depends(get_db)):
    rooms = db.query(models.Room).all()
    return rooms

# Endpoint to get a single room by ID
@router.get(
    "/{room_id}",
    response_model=schemas.Room,
    summary="Get a single room",
    description="Retrieve a single cinema room by its unique ID. Returns a 404 error if the room is not found."
)
def get_room(
    room_id: int = Path(..., description="The unique ID of the room to retrieve."),
    db: Session = Depends(get_db)
):
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
    description="Creates a new cinema room with a unique name and seating dimensions. A conflict error is returned if a room with the same name already exists."
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
    description="Updates an existing room's details, such as name and seating capacity. An update is only possible if the room does not have any existing schedules."
)
def update_room(
    room: schemas.RoomCreate,
    room_id: int = Path(..., description="The unique ID of the room to update."),
    db: Session = Depends(get_db)
):
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
    description="Deletes a room by its ID. This operation is only permitted if the room has no existing schedules to prevent data integrity issues."
)
def delete_room(
    room_id: int = Path(..., description="The unique ID of the room to delete."),
    db: Session = Depends(get_db)
):
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