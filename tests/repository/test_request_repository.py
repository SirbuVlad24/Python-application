import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.repositories.request_repository import get_requests, save_request


def test_request_can_be_saved_and_has_id_and_created_at(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()

    saved = save_request(session, "power", {"base": 2, "exponent": 10}, 1024)

    assert saved.id
    assert saved.created_at is not None
    assert saved.operation == "power"
    session.close()


def test_requests_persist_after_session_is_closed_and_reopened(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)

    first_session = session_factory()
    saved = save_request(
        first_session,
        "power",
        {"base": 2, "exponent": 10},
        1024,
    )
    first_session.close()

    second_session = session_factory()
    requests = get_requests(second_session)

    assert requests == [
        {
            "id": saved.id,
            "operation": "power",
            "input": {"base": 2, "exponent": 10},
            "result": 1024,
            "created_at": saved.created_at.isoformat(),
        }
    ]
    second_session.close()


def test_each_saved_request_has_a_unique_id(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()

    first = save_request(session, "fibonacci", {"n": 10}, 55)
    second = save_request(session, "factorial", {"n": 5}, 120)

    assert first.id != second.id
    session.close()


def test_input_data_is_stored_as_json_and_restored(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()

    saved = save_request(session, "power", {"exponent": 10, "base": 2}, 1024)
    requests = get_requests(session)

    assert json.loads(saved.input_data) == {"base": 2, "exponent": 10}
    assert requests[0]["input"] == {"base": 2, "exponent": 10}
    session.close()