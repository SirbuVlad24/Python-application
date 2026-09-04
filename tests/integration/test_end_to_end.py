import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes import get_db
from app.database import Base
from app.main import app
from app.services.math_service import (
    MAX_EXPONENT,
    MAX_FACTORIAL_N,
    MAX_FIBONACCI_N,
)


@pytest.fixture
def integration_client(tmp_path):
    """Create an isolated API client with a temporary SQLite database."""
    database_url = f"sqlite:///{tmp_path / 'test_integration.db'}"

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

    def override_get_db():
        db = test_session()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
    engine.dispose()


def assert_calculation_response(response, operation, input_data, result):
    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["id"], str)
    assert data["id"]
    assert data["operation"] == operation
    assert data["input"] == input_data
    assert data["result"] == result


def test_power_end_to_end_and_persistence(integration_client):
    response = integration_client.post(
        "/power",
        json={"base": 2, "exponent": 10},
    )

    assert_calculation_response(
        response,
        "power",
        {"base": 2, "exponent": 10},
        1024,
    )

    history_response = integration_client.get("/requests")

    assert history_response.status_code == 200
    history = history_response.json()

    assert len(history) == 1
    assert history[0]["operation"] == "power"
    assert history[0]["input"] == {"base": 2, "exponent": 10}
    assert history[0]["result"] == 1024
    assert history[0]["created_at"]


def test_fibonacci_end_to_end_and_persistence(integration_client):
    response = integration_client.post(
        "/fibonacci",
        json={"n": 10},
    )

    assert_calculation_response(
        response,
        "fibonacci",
        {"n": 10},
        55,
    )

    history_response = integration_client.get("/requests")

    assert history_response.status_code == 200
    history = history_response.json()

    assert len(history) == 1
    assert history[0]["operation"] == "fibonacci"
    assert history[0]["result"] == 55
    assert history[0]["created_at"]


def test_factorial_end_to_end_and_persistence(integration_client):
    response = integration_client.post(
        "/factorial",
        json={"n": 5},
    )

    assert_calculation_response(
        response,
        "factorial",
        {"n": 5},
        120,
    )

    history_response = integration_client.get("/requests")

    assert history_response.status_code == 200
    history = history_response.json()

    assert len(history) == 1
    assert history[0]["operation"] == "factorial"
    assert history[0]["result"] == 120
    assert history[0]["created_at"]


def test_request_history_contains_all_operations(integration_client):
    responses = [
        integration_client.post(
            "/power",
            json={"base": 2, "exponent": 10},
        ),
        integration_client.post(
            "/fibonacci",
            json={"n": 10},
        ),
        integration_client.post(
            "/factorial",
            json={"n": 5},
        ),
    ]

    assert all(response.status_code == 200 for response in responses)

    history_response = integration_client.get("/requests")

    assert history_response.status_code == 200
    history = history_response.json()

    assert len(history) == 3
    assert {request["operation"] for request in history} == {
        "power",
        "fibonacci",
        "factorial",
    }

    for request in history:
        assert isinstance(request["id"], str)
        assert request["id"]
        assert isinstance(request["operation"], str)
        assert isinstance(request["input"], dict)
        assert request["result"] is not None
        assert isinstance(request["created_at"], str)
        assert request["created_at"]


def test_empty_request_history(integration_client):
    response = integration_client.get("/requests")

    assert response.status_code == 200
    assert response.json() == []


def test_request_ids_are_unique(integration_client):
    first_response = integration_client.post(
        "/power",
        json={"base": 2, "exponent": 10},
    )
    second_response = integration_client.post(
        "/power",
        json={"base": 2, "exponent": 10},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json()["id"] != second_response.json()["id"]


@pytest.mark.parametrize(
    ("endpoint", "payload", "expected_result"),
    [
        ("/power", {"base": 0, "exponent": 5}, 0),
        ("/power", {"base": 5, "exponent": 0}, 1),
        ("/fibonacci", {"n": 0}, 0),
        ("/fibonacci", {"n": 1}, 1),
        ("/factorial", {"n": 0}, 1),
        ("/factorial", {"n": 1}, 1),
    ],
)
def test_edge_values_are_accepted(
    integration_client,
    endpoint,
    payload,
    expected_result,
):
    response = integration_client.post(endpoint, json=payload)

    assert response.status_code == 200
    assert response.json()["result"] == expected_result


@pytest.mark.parametrize(
    ("endpoint", "payload"),
    [
        ("/power", {"base": 2, "exponent": -1}),
        ("/fibonacci", {"n": -1}),
        ("/factorial", {"n": -1}),
        ("/power", {"base": 2, "exponent": MAX_EXPONENT + 1}),
        ("/fibonacci", {"n": MAX_FIBONACCI_N + 1}),
        ("/factorial", {"n": MAX_FACTORIAL_N + 1}),
    ],
)
def test_invalid_values_are_rejected_and_not_saved(
    integration_client,
    endpoint,
    payload,
):
    response = integration_client.post(endpoint, json=payload)

    assert response.status_code == 422
    assert "detail" in response.json()

    history_response = integration_client.get("/requests")

    assert history_response.status_code == 200
    assert history_response.json() == []


@pytest.mark.parametrize(
    ("endpoint", "payload"),
    [
        ("/power", {"exponent": 10}),
        ("/power", {"base": 2}),
        ("/fibonacci", {}),
        ("/factorial", {}),
        ("/fibonacci", {"n": "ten"}),
        ("/factorial", {"n": True}),
    ],
)
def test_malformed_payloads_are_rejected(
    integration_client,
    endpoint,
    payload,
):
    response = integration_client.post(endpoint, json=payload)

    assert response.status_code == 422
    assert "detail" in response.json()


def test_unknown_endpoint_returns_not_found(integration_client):
    response = integration_client.get("/unknown-endpoint")

    assert response.status_code == 404


def test_wrong_http_method_returns_method_not_allowed(integration_client):
    response = integration_client.get("/power")

    assert response.status_code == 405
def test_invalid_json_returns_a_client_error(integration_client):
    response = integration_client.post(
        "/power",
        content='{"base": 2, "exponent":',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code in {400, 422}


def test_unexpected_internal_error_returns_500(
    integration_client,
    monkeypatch,
):
    def failing_save_request(*args, **kwargs):
        raise RuntimeError("simulated database failure")

    monkeypatch.setattr(
        "app.api.routes.save_request",
        failing_save_request,
    )

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/power",
            json={"base": 2, "exponent": 10},
        )

    assert response.status_code == 500