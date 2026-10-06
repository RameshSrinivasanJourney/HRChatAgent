# HR Chat Agent - Phase 1

Secure HR backend foundation for the Agentic AI HR Chat Agent assessment.

## Phase 1 scope

- FastAPI
- SQLite
- SQLAlchemy
- JWT authentication
- Employee authorization context
- Employee profile endpoint
- Leave balance endpoint
- Automated tests

## Setup

Create virtual environment:

```powershell
python -m venv .venv
```

Install dependencies:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Seed database:

```powershell
.venv\Scripts\python.exe scripts_seed.py
```

Start API:

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Swagger:

http://127.0.0.1:8000/docs

Run tests:

```powershell
.venv\Scripts\python.exe -m pytest -q
```

## Test users

All users use:

```text
Password@123
```

Employees:

```text
EMP1001 - Active
EMP1002 - Active
EMP1003 - Notice Period
```

## Phase 1 security principle

The authenticated employee identity is obtained from the JWT `sub` claim.

The leave endpoint does NOT accept an arbitrary employee ID from the caller.

This prevents:

```text
Employee A -> request Employee B's leave balance
```

The authenticated identity will later flow into the HR Agent tools.
