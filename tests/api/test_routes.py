import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes import get_db
from app.database import Base
from app.main import app


# Create a separate temporary database for the API tests
@pytest.fixture
def client(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'test_api.db'}"

    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    test_session = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    # Replace the normal database with the temporary test database
    def override_get_db():
        db = test_session()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Remove the replacement after the test finishes
    app.dependency_overrides.clear()


# Test the power endpoint
def test_power_endpoint(client):
    response = client.post(
        "/power",
        json={"base": 2, "exponent": 10},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["operation"] == "power"
    assert data["input"] == {
        "base": 2,
        "exponent": 10,
    }
    assert data["result"] == 1024
    assert data["id"]


# Test the Fibonacci endpoint
def test_fibonacci_endpoint(client):
    response = client.post(
        "/fibonacci",
        json={"n": 10},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["operation"] == "fibonacci"
    assert data["result"] == 55
    assert data["id"]


# Test the factorial endpoint
def test_factorial_endpoint(client):
    response = client.post(
        "/factorial",
        json={"n": 5},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["operation"] == "factorial"
    assert data["result"] == 120
    assert data["id"]


# Test that a negative number is rejected
def test_negative_fibonacci_value_is_rejected(client):
    response = client.post(
        "/fibonacci",
        json={"n": -1},
    )

    assert response.status_code == 422
    assert "negative" in response.json()["detail"]


# Test that a missing field is rejected
def test_missing_required_field_is_rejected(client):
    response = client.post(
        "/factorial",
        json={},
    )

    assert response.status_code == 422


# Test that the request appears in the history
def test_request_history(client):
    client.post(
        "/power",
        json={"base": 2, "exponent": 10},
    )

    response = client.get("/requests")

    assert response.status_code == 200

    history = response.json()
    assert len(history) == 1
    assert history[0]["operation"] == "power"
    assert history[0]["result"] == 1024
    assert history[0]["input"] == {
        "base": 2,
        "exponent": 10,
    }
    assert history[0]["created_at"]