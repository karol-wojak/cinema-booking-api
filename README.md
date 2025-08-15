# Cinema Booking API

Welcome to the Cinema Booking API, a FastAPI-based backend for managing cinema rooms, movies, schedules, and seat bookings. This project is built using Python, FastAPI, and SQLAlchemy to provide a robust and scalable foundation for a modern cinema platform.

## Features

- **Room Management**: Create and retrieve cinema rooms with specified row and seat capacities.
- **Movie Catalog**: Add and manage movies with titles and poster images.
- **Flexible Scheduling**: Schedule movies for specific dates and times in any room.
- **Booking System**: Book seats for a movie's session, with real-time seat availability checks.
- **Optimized Endpoints**: Efficient data retrieval using joinedload to prevent unnecessary database queries.

## Local Project Setup

Follow these steps to get the project up and running on your local machine.

### 1. Prerequisites

Make sure you have the following installed:

- Python 3.11+
- Git

### 2. Clone the Repository

Clone the project from your Git repository:

```bash
git clone https://github.com/karol-wojak/cinema-booking-api
cd cinema-booking-api
```

### 3. Create a Virtual Environment

It's a best practice to use a virtual environment to manage dependencies.

```bash
# On Windows
python -m venv .venv

# On macOS / Linux
python3 -m venv .venv
```

Activate the virtual environment:

```bash
# On Windows
.venv\Scripts\activate

# On macOS / Linux
source .venv/bin/activate
```

### 4. Install Dependencies

Install all the necessary Python packages using pip.

```bash
pip install -r requirements.txt
```

### 5. Run the Application

Start the FastAPI application. This command will launch a local server and automatically reload it when you make code changes.

```bash
uvicorn app.main:app --reload
```

The API will be available at http://127.0.0.1:8000.

### 6. Access the Interactive API Docs

You can access the interactive API documentation at the following URL. This interface allows you to explore and test all available endpoints.

**Swagger UI**: http://127.0.0.1:8000/docs