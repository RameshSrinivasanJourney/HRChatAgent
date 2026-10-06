import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    from app.database import SessionLocal
    from app.models import Employee, LeaveBalance
    from app.security import hash_password

    db = SessionLocal()

    password_hash = hash_password("Password@123")

    employees = [
        Employee(
            employee_id="EMP1001",
            name="Arun Kumar",
            email="arun@example.com",
            department="Engineering",
            role="Senior Developer",
            status="ACTIVE",
            password_hash=password_hash,
        ),
        Employee(
            employee_id="EMP1002",
            name="Priya Sharma",
            email="priya@example.com",
            department="HR",
            role="HR Specialist",
            status="ACTIVE",
            password_hash=password_hash,
        ),
        Employee(
            employee_id="EMP1003",
            name="Rahul Menon",
            email="rahul@example.com",
            department="Engineering",
            role="Lead Developer",
            status="NOTICE_PERIOD",
            password_hash=password_hash,
        ),
    ]

    db.add_all(employees)
    db.flush()

    balances = [
        LeaveBalance(employee_id="EMP1001", leave_type="CL",
                     entitlement=12, used=5, remaining=7),
        LeaveBalance(employee_id="EMP1001", leave_type="EL",
                     entitlement=8, used=2, remaining=14),
        LeaveBalance(employee_id="EMP1001", leave_type="PL",
                     entitlement=0, used=0, remaining=13),
        LeaveBalance(employee_id="EMP1002", leave_type="CL",
                     entitlement=12, used=8, remaining=4),
        LeaveBalance(employee_id="EMP1002", leave_type="EL",
                     entitlement=8, used=0, remaining=20),
        LeaveBalance(employee_id="EMP1002", leave_type="PL",
                     entitlement=0, used=0, remaining=6),
        LeaveBalance(employee_id="EMP1003", leave_type="CL",
                     entitlement=12, used=2, remaining=10),
        LeaveBalance(employee_id="EMP1003", leave_type="EL",
                     entitlement=8, used=0, remaining=20),
        LeaveBalance(employee_id="EMP1003", leave_type="PL",
                     entitlement=0, used=0, remaining=10),
    ]

    db.add_all(balances)
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)
