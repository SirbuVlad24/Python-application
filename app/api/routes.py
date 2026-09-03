from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repositories.request_repository import get_requests, save_request
from app.schemas.requests import (
    CalculationResponse,
    HistoryResponse,
    NumberRequest,
    PowerRequest,
)
from app.services.math_service import (
    MathValidationError,
    factorial,
    fibonacci,
    power,
)


router = APIRouter()


# Provides a database session for each API request
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# Converts validation errors into a clear HTTP 422 response
def validation_error(error: MathValidationError) -> HTTPException:
    return HTTPException(
        status_code=422,
        detail=str(error),
    )


# POST /power
@router.post("/power", response_model=CalculationResponse)
def calculate_power(
    data: PowerRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        result = power(data.base, data.exponent)
    except MathValidationError as error:
        raise validation_error(error) from error

    input_data = data.model_dump()
    saved_request = save_request(db, "power", input_data, result)

    return {
        "id": saved_request.id,
        "operation": "power",
        "input": input_data,
        "result": result,
    }


# POST /fibonacci
@router.post("/fibonacci", response_model=CalculationResponse)
def calculate_fibonacci(
    data: NumberRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        result = fibonacci(data.n)
    except MathValidationError as error:
        raise validation_error(error) from error

    input_data = data.model_dump()
    saved_request = save_request(db, "fibonacci", input_data, result)

    return {
        "id": saved_request.id,
        "operation": "fibonacci",
        "input": input_data,
        "result": result,
    }


# POST /factorial
@router.post("/factorial", response_model=CalculationResponse)
def calculate_factorial(
    data: NumberRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        result = factorial(data.n)
    except MathValidationError as error:
        raise validation_error(error) from error

    input_data = data.model_dump()
    saved_request = save_request(db, "factorial", input_data, result)

    return {
        "id": saved_request.id,
        "operation": "factorial",
        "input": input_data,
        "result": result,
    }


# GET /requests
@router.get("/requests", response_model=list[HistoryResponse])
def request_history(
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    return get_requests(db)