from fastapi import APIRouter, Depends

from app.dependencies import get_current_employee
from app.models import Employee
from app.schemas import EmployeeResponse

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("/me", response_model=EmployeeResponse)
def get_my_profile(
    employee: Employee = Depends(get_current_employee)
):
    return employee
