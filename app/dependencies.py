from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee
from app.security import decode_access_token

security = HTTPBearer()


def get_current_employee(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        employee_id = decode_access_token(credentials.credentials)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token"
        )

    employee = (
        db.query(Employee)
        .filter(Employee.employee_id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated employee not found"
        )

    return employee
