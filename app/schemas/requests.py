from datetime import datetime
from typing import Any

from pydantic import BaseModel, StrictFloat, StrictInt


# Data required by POST /power
class PowerRequest(BaseModel):
    base: StrictInt | StrictFloat
    exponent: StrictInt


# Data required by POST /fibonacci and POST /factorial
class NumberRequest(BaseModel):
    n: StrictInt


# Response returned after a successful calculation
class CalculationResponse(BaseModel):
    id: str
    operation: str
    input: dict[str, Any]
    result: int | float


# Response returned by GET /requests
class HistoryResponse(CalculationResponse):
    created_at: datetime