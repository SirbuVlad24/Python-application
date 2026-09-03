# REST Microservice for Mathematical Operations

A Python REST microservice that performs mathematical operations and stores the history of processed requests in an SQLite database.

## Features

The service supports:

- calculating a power: `base^exponent`;
- calculating the n-th Fibonacci number;
- calculating a factorial: `n!`;
- retrieving the history of processed requests.

## Technologies

- Python
- FastAPI
- SQLite
- Pytest
- JSON REST API

## Project Structure

```text
project-root/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── requests.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── math_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── request_repository.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── request.py
│   └── database.py
├── tests/
│   ├── unit/
│   ├── repository/
│   ├── api/
│   └── integration/
├── requirements.txt
├── README.md
├── Dockerfile
└── .gitignore
```

The application is divided into three main layers:

- `api` - defines the REST endpoints;
- `services` - contains the mathematical business logic;
- `repositories` and `database` - handle data persistence.

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd <repository-folder>
```

Create and activate a virtual environment.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Interactive documentation is available at `http://127.0.0.1:8000/docs`.

## API Endpoints

### POST `/power`

Calculates `base^exponent`.

Request:

```json
{
  "base": 2,
  "exponent": 10
}
```

Response:

```json
{
  "id": "<unique-id>",
  "operation": "power",
  "input": {"base": 2, "exponent": 10},
  "result": 1024
}
```

### POST `/fibonacci`

Calculates the Fibonacci number at index `n`.

Request:

```json
{"n": 10}
```

Response:

```json
{
  "id": "<unique-id>",
  "operation": "fibonacci",
  "input": {"n": 10},
  "result": 55
}
```

Fibonacci uses zero-based indexing: `F(0) = 0` and `F(1) = 1`.

### POST `/factorial`

Calculates `n!`.

Request:

```json
{"n": 5}
```

Response:

```json
{
  "id": "<unique-id>",
  "operation": "factorial",
  "input": {"n": 5},
  "result": 120
}
```

The service supports `0! = 1` and `1! = 1`.

### GET `/requests`

Returns the history of processed requests.

Response:

```json
[
  {
    "id": "<unique-id>",
    "operation": "power",
    "input": {"base": 2, "exponent": 10},
    "result": 1024,
    "created_at": "2026-09-03T12:00:00Z"
  }
]
```

## Validation and Error Handling

- Fibonacci and factorial accept only non-negative integers.
- The exponent must be a non-negative integer.
- Negative values, invalid types, incomplete JSON, and values above the configured limits are rejected.
- `200 OK` is returned for successful requests.
- `422 Unprocessable Entity` is returned for invalid input.
- `500 Internal Server Error` is used for unexpected errors without exposing internal details.

The exact limits are maintained in the business logic and must be confirmed by the team before final delivery.

## Data Persistence

Each processed request is saved in SQLite with:

- a unique identifier;
- the performed operation;
- the input values;
- the calculation result;
- the processing date and time.

## Testing

Run all tests with:

```bash
python -m pytest -q
```

Tests cover normal cases, values `0` and `1`, negative values, values above the limits, invalid input types, persistence, API responses, and request history.

## Technical Decisions

FastAPI was selected for simple REST endpoint creation, JSON validation, interactive documentation, and automated API testing.

SQLite was selected because it is lightweight, file-based, and suitable for a small academic project.

The API, business logic, and data access layers are separated to make the application easier to test, maintain, and extend. Mathematical services return only calculation results and do not depend on FastAPI or SQLite.

## Team Branches

- `feature/math-services` - mathematical functions, validation, and unit tests;
- `feature/database-repository` - SQLite database and data access;
- `feature/rest-api` - FastAPI endpoints and API tests;
- `feature/integration-release` - integration, documentation, and final delivery.

## Optional Bonuses

Optional features may be implemented after all mandatory requirements are complete:

- Docker containerization;
- a simple web interface;
- caching;
- logging and monitoring;
- simple authentication;
- a serverless or messaging-system version.
