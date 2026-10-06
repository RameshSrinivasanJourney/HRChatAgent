from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_employee
from app.models import Employee, LeaveBalance
from app.schemas import LeaveBalanceResponse

router = APIRouter(prefix="/leave", tags=["Leave"])


@router.get(
    "/balance/{leave_type}",
    response_model=LeaveBalanceResponse
)
def get_leave_balance(
    leave_type: str,
    employee: Employee = Depends(get_current_employee),
    db: Session = Depends(get_db)
):
    leave_type = leave_type.upper()

    balance = (
        db.query(LeaveBalance)
        .filter(
            LeaveBalance.employee_id == employee.employee_id,
            LeaveBalance.leave_type == leave_type
        )
        .first()
    )

    if not balance:
        raise HTTPException(
            status_code=404,
            detail=f"No {leave_type} leave balance found"
        )

    return balance
