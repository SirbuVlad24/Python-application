from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = f"sqlite:///{Path(__file__).resolve().parent.parent / 'requests.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def create_tables() -> None:
    """Create all tables registered on Base."""
    from app.models.request import Request  # noqa: F401

    Base.metadata.create_all(bind=engine)