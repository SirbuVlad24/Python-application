from fastapi import FastAPI

from app.api.routes import router
from app.database import create_tables


# Create the database table when the application starts
create_tables()

# Create the FastAPI application
app = FastAPI(
    title="Mathematical Operations API",
    description="REST API for power, Fibonacci, and factorial calculations.",
    version="1.0.0",
)

# Add all API endpoints
app.include_router(router)