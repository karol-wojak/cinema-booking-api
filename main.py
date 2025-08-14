from fastapi import FastAPI
from app.database import engine, Base
from app.routers import rooms, bookings

# Create all tables in the database.
# This should only be done when you first start the application.
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(rooms.router)
app.include_router(bookings.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}