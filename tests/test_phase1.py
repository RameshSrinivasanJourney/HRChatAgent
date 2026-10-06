from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def login(employee_id="EMP1001", password="Password@123"):
    response = client.post(
        "/auth/login",
        json={
            "employee_id": employee_id,
            "password": password
        }
    )

    return response


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_invalid_login():
    response = login(password="WrongPassword")

    assert response.status_code == 401


def test_successful_login():
    response = login()

    assert response.status_code == 200

    body = response.json()

    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_authenticated_employee_profile():
    response = login()

    token = response.json()["access_token"]

    response = client.get(
        "/employees/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert body["employee_id"] == "EMP1001"
    assert body["name"] == "Arun Kumar"
    assert body["status"] == "ACTIVE"


def test_leave_balance_requires_authentication():
    response = client.get("/leave/balance/CL")

    assert response.status_code == 403


def test_authenticated_leave_balance():
    response = login()

    token = response.json()["access_token"]

    response = client.get(
        "/leave/balance/CL",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert body["employee_id"] == "EMP1001"
    assert body["leave_type"] == "CL"
    assert body["entitlement"] == 12
    assert body["used"] == 5
    assert body["remaining"] == 7


def test_notice_period_employee_can_authenticate():
    response = login(employee_id="EMP1003")

    assert response.status_code == 200

    token = response.json()["access_token"]

    profile = client.get(
        "/employees/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert profile.status_code == 200
    assert profile.json()["status"] == "NOTICE_PERIOD"
