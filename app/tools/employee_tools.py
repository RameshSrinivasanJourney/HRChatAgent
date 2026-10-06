from sqlalchemy.orm import Session

from app.models import Employee


class EmployeeTools:
    """
    Employee-specific tools.

    These tools read employee information from the database.
    The employee_id should come from the authenticated user context,
    not directly from the user's chat message.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_employee_profile(self, employee_id: str) -> dict:
        employee = (
            self.db.query(Employee)
            .filter(Employee.employee_id == employee_id)
            .first()
        )

        if employee is None:
            raise ValueError("Employee not found.")

        return {
            "employee_id": employee.employee_id,
            "name": employee.name,
            "email": employee.email,
            "department": employee.department,
            "role": employee.role,
            "status": employee.status,
        }