from sqlalchemy.orm import Session

from app.tools.employee_tools import EmployeeTools
from app.tools.leave_tools import (
    LeaveTools,
    LeaveCalculationTool,
    PLConversionTool,
    LeaveEligibilityTool,
)


class HRToolRegistry:

    def __init__(self, db: Session):
        self.db = db

        self.employee_tools = EmployeeTools(db)
        self.leave_tools = LeaveTools(db)

        self.leave_calculator = LeaveCalculationTool()
        self.pl_conversion = PLConversionTool()
        self.leave_eligibility = LeaveEligibilityTool()

    def get_employee_profile(
        self,
        employee_id: str
    ) -> dict:

        return self.employee_tools.get_employee_profile(
            employee_id
        )

    def get_leave_balance(
        self,
        employee_id: str
    ) -> dict:

        return self.leave_tools.get_leave_balance(
            employee_id
        )

    def get_specific_leave_balance(
        self,
        employee_id: str,
        leave_type: str
    ) -> dict:

        return self.leave_tools.get_balance(
            employee_id,
            leave_type
        )

    def calculate_leave_balance(
        self,
        current_balance: float,
        requested_days: float
    ) -> dict:

        return self.leave_calculator.calculate_remaining_balance(
            current_balance,
            requested_days
        )

    def calculate_pl_conversion(
        self,
        pl_balance: int
    ) -> dict:

        return self.pl_conversion.calculate(
            pl_balance
        )

    def check_leave_eligibility(
        self,
        leave_type: str,
        requested_days: float,
        current_balance: float
    ) -> dict:

        return self.leave_eligibility.check(
            leave_type,
            requested_days,
            current_balance
        )