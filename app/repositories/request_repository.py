import json
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.request import Request


def save_request(
    db: Session,
    operation: str,
    input_data: dict[str, Any],
    result: Any,
) -> Request:
    request = Request(
        id=str(uuid4()),
        operation=operation,
        input_data=json.dumps(input_data, sort_keys=True),
        result=json.dumps(result),
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def get_requests(db: Session) -> list[dict[str, Any]]:
    requests = db.query(Request).order_by(Request.created_at, Request.id).all()
    return [
        {
            "id": request.id,
            "operation": request.operation,
            "input": json.loads(request.input_data),
            "result": json.loads(request.result),
            "created_at": request.created_at.isoformat(),
        }
        for request in requests
    ]