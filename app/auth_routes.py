from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee
from app.schemas import LoginRequest, TokenResponse
from app.security import verify_password, create_access_token

from app.logging_config import get_logger


logger = get_logger("hr_chat.auth")


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    employee = (
        db.query(Employee)
        .filter(
            Employee.employee_id == request.employee_id
        )
        .first()
    )

    if not employee or not verify_password(
        request.password,
        employee.password_hash,
    ):
        logger.warning(
            "login_failed employee_id=%s",
            request.employee_id,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid employee ID or password",
        )

    token = create_access_token(
        employee.employee_id
    )

    logger.info(
        "login_success employee_id=%s",
        employee.employee_id,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }