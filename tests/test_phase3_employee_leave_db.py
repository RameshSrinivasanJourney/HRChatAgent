import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Employee, LeaveBalance
from app.tools.employee_tools import EmployeeTools
from app.tools.leave_tools import LeaveTools


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={
            "check_same_thread": False
        }
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    employee = Employee(
        employee_id="EMP001",
        name="Test Employee",
        email="test.employee@company.com",
        department="IT",
        role="Developer",
        status="ACTIVE",
        password_hash="test-hash",
    )

    db.add(employee)

    db.add_all([
        LeaveBalance(
            employee_id="EMP001",
            leave_type="CL",
            entitlement=12,
            used=4,
            remaining=8,
        ),
        LeaveBalance(
            employee_id="EMP001",
            leave_type="EL",
            entitlement=8,
            used=2,
            remaining=6,
        ),
        LeaveBalance(
            employee_id="EMP001",
            leave_type="PL",
            entitlement=0,
            used=0,
            remaining=10,
        ),
    ])

    db.commit()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)


def test_get_employee_profile(db_session):

    tools = EmployeeTools(db_session)

    result = tools.get_employee_profile("EMP001")

    assert result["employee_id"] == "EMP001"
    assert result["name"] == "Test Employee"
    assert result["department"] == "IT"
    assert result["status"] == "ACTIVE"


def test_employee_not_found(db_session):

    tools = EmployeeTools(db_session)

    with pytest.raises(ValueError):
        tools.get_employee_profile("INVALID")


def test_get_all_leave_balances(db_session):

    tools = LeaveTools(db_session)

    result = tools.get_leave_balance("EMP001")

    assert result["employee_id"] == "EMP001"

    assert result["leaves"]["CL"]["entitlement"] == 12
    assert result["leaves"]["CL"]["used"] == 4
    assert result["leaves"]["CL"]["remaining"] == 8

    assert result["leaves"]["EL"]["entitlement"] == 8
    assert result["leaves"]["EL"]["used"] == 2
    assert result["leaves"]["EL"]["remaining"] == 6

    assert result["leaves"]["PL"]["remaining"] == 10


def test_get_specific_leave_balance(db_session):

    tools = LeaveTools(db_session)

    result = tools.get_balance(
        "EMP001",
        "CL"
    )

    assert result["leave_type"] == "CL"
    assert result["entitlement"] == 12
    assert result["used"] == 4
    assert result["remaining"] == 8


def test_specific_leave_type_is_case_insensitive(db_session):

    tools = LeaveTools(db_session)

    result = tools.get_balance(
        "EMP001",
        "cl"
    )

    assert result["leave_type"] == "CL"
    assert result["remaining"] == 8


def test_leave_balance_not_found(db_session):

    tools = LeaveTools(db_session)

    with pytest.raises(ValueError):
        tools.get_balance(
            "EMP001",
            "SL"
        )