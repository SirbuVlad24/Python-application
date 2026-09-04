from fastapi import FastAPI

from app.api.routes import router
from app.database import create_tables
from fastapi.middleware.cors import CORSMiddleware

# Create the database table when the application starts
create_tables()

# Create the FastAPI application
app = FastAPI(
    title="Mathematical Operations API",
    description="REST API for power, Fibonacci, and factorial calculations.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# Add all API endpoints
app.include_router(router)