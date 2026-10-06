from sqlalchemy.orm import Session

from app.models import LeaveBalance


class LeaveTools:
    """
    Database-backed employee leave tools.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_leave_balance(self, employee_id: str) -> dict:
        balances = (
            self.db.query(LeaveBalance)
            .filter(LeaveBalance.employee_id == employee_id)
            .all()
        )

        if not balances:
            raise ValueError("Leave balance not found.")

        result = {
            "employee_id": employee_id,
            "leaves": {}
        }

        for balance in balances:
            result["leaves"][balance.leave_type.upper()] = {
                "entitlement": balance.entitlement,
                "used": balance.used,
                "remaining": balance.remaining,
            }

        return result

    def get_balance(
        self,
        employee_id: str,
        leave_type: str
    ) -> dict:
        leave_type = leave_type.upper().strip()

        balance = (
            self.db.query(LeaveBalance)
            .filter(
                LeaveBalance.employee_id == employee_id,
                LeaveBalance.leave_type == leave_type
            )
            .first()
        )

        if balance is None:
            raise ValueError(
                f"{leave_type} leave balance not found."
            )

        return {
            "employee_id": employee_id,
            "leave_type": leave_type,
            "entitlement": balance.entitlement,
            "used": balance.used,
            "remaining": balance.remaining,
        }


class LeaveCalculationTool:
    """
    Deterministic leave calculations.
    """

    @staticmethod
    def calculate_remaining_balance(
        current_balance: float,
        requested_days: float,
    ) -> dict:

        if current_balance < 0:
            raise ValueError(
                "Current balance cannot be negative."
            )

        if requested_days <= 0:
            raise ValueError(
                "Requested leave must be greater than zero."
            )

        if requested_days > current_balance:
            return {
                "eligible": False,
                "current_balance": current_balance,
                "requested_days": requested_days,
                "remaining_balance": current_balance,
                "message": "Insufficient leave balance.",
            }

        remaining = current_balance - requested_days

        return {
            "eligible": True,
            "current_balance": current_balance,
            "requested_days": requested_days,
            "remaining_balance": remaining,
            "message": "Leave balance is sufficient.",
        }


class PLConversionTool:
    """
    Implements the PL -> EL conversion rule from the HR policy.

    Rules:
    - PL <= 6: no conversion
    - Even PL > 6: retain 6
    - Odd PL > 6: retain 7
    - Remaining PL converts to EL at 2:1
    """

    @staticmethod
    def calculate(pl_balance: int) -> dict:

        if pl_balance < 0:
            raise ValueError(
                "PL balance cannot be negative."
            )

        if pl_balance <= 6:
            return {
                "original_pl": pl_balance,
                "retained_pl": pl_balance,
                "converted_pl": 0,
                "el_credit": 0,
                "conversion_applied": False,
            }

        retained_pl = (
            6
            if pl_balance % 2 == 0
            else 7
        )

        convertible_pl = pl_balance - retained_pl

        el_credit = convertible_pl // 2

        return {
            "original_pl": pl_balance,
            "retained_pl": retained_pl,
            "converted_pl": convertible_pl,
            "el_credit": el_credit,
            "conversion_applied": True,
        }


class LeaveEligibilityTool:
    """
    Basic balance-based leave eligibility.

    This is intentionally deterministic.

    More advanced policy conditions such as:
    - probation completion
    - EL encashment
    - notice-period restrictions
    - maternity/paternity/adoption rules

    will be handled by combining employee data,
    policy retrieval and deterministic rules in the agent layer.
    """

    SUPPORTED_LEAVE_TYPES = {
        "CL",
        "EL",
        "PL",
    }

    @staticmethod
    def check(
        leave_type: str,
        requested_days: float,
        current_balance: float,
    ) -> dict:

        leave_type = leave_type.upper().strip()

        if requested_days <= 0:
            return {
                "eligible": False,
                "reason": (
                    "Requested leave must be greater than zero."
                ),
            }

        if leave_type not in LeaveEligibilityTool.SUPPORTED_LEAVE_TYPES:
            return {
                "eligible": False,
                "reason": "Unsupported leave category.",
            }

        if current_balance < 0:
            return {
                "eligible": False,
                "reason": "Current balance cannot be negative.",
            }

        if requested_days > current_balance:
            return {
                "eligible": False,
                "leave_type": leave_type,
                "current_balance": current_balance,
                "requested_days": requested_days,
                "reason": (
                    f"Insufficient {leave_type} leave balance."
                ),
            }

        remaining_balance = (
            current_balance - requested_days
        )

        return {
            "eligible": True,
            "leave_type": leave_type,
            "current_balance": current_balance,
            "requested_days": requested_days,
            "remaining_balance": remaining_balance,
            "reason": "Sufficient leave balance.",
        }