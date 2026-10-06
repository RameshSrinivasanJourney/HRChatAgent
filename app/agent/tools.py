from typing import Any

from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.agent.audit import ToolAuditContext
from app.tools.employee_tools import EmployeeTools
from app.tools.leave_tools import (
    LeaveTools,
    LeaveCalculationTool,
    PLConversionTool,
    LeaveEligibilityTool,
)
from app.tools.policy_tools import create_policy_search_tool


def create_hr_tools(
    db: Session,
    employee_id: str,
    correlation_id: str,
    conversation_id: str | None = None,
):
    """
    Create HR tools for the authenticated employee.

    Security:
    - employee_id comes from the authenticated session.
    - The LLM/user cannot provide an employee ID to access another employee.
    - Audit information is attached to every tool execution.
    """

    employee_tools = EmployeeTools(db)
    leave_tools = LeaveTools(db)
    policy_search_tool = create_policy_search_tool()

    # =========================================================
    # 1. GET EMPLOYEE PROFILE
    # =========================================================

    @tool
    def get_employee_profile() -> dict[str, Any]:
        """
        Get the authenticated employee's profile.

        Use this tool when the user asks about their:
        - name
        - email
        - department
        - role
        - employment status

        Never accept an employee ID from the user.
        The employee ID is taken from the authenticated session.
        """

        with ToolAuditContext(
            db,
            correlation_id=correlation_id,
            conversation_id=conversation_id,
            employee_id=employee_id,
            tool_name="get_employee_profile",
        ):
            return employee_tools.get_employee_profile(
                employee_id
            )

    # =========================================================
    # 2. GET ALL LEAVE BALANCES
    # =========================================================

    @tool
    def get_leave_balance() -> dict[str, Any]:
        """
        Get the authenticated employee's CL, EL and PL leave
        balances.

        Use this tool when the user asks:
        - How much leave do I have?
        - What is my leave balance?
        - Show my leave balances.
        """

        with ToolAuditContext(
            db,
            correlation_id=correlation_id,
            conversation_id=conversation_id,
            employee_id=employee_id,
            tool_name="get_leave_balance",
        ):
            return leave_tools.get_leave_balance(
                employee_id
            )

    # =========================================================
    # 3. GET SPECIFIC LEAVE BALANCE
    # =========================================================

    @tool
    def get_specific_leave_balance(
        leave_type: str,
    ) -> dict[str, Any]:
        """
        Get the authenticated employee's balance for a
        specific leave type.

        Supported leave types:
        - CL
        - EL
        - PL

        Example:
            EL
        """

        with ToolAuditContext(
            db,
            correlation_id=correlation_id,
            conversation_id=conversation_id,
            employee_id=employee_id,
            tool_name="get_specific_leave_balance",
        ):
            return leave_tools.get_balance(
                employee_id,
                leave_type,
            )

    # =========================================================
    # 4. CALCULATE REMAINING LEAVE
    # =========================================================

    @tool
    def calculate_remaining_leave(
        current_balance: float,
        requested_days: float,
    ) -> dict[str, Any]:
        """
        Calculate remaining leave deterministically.

        IMPORTANT:
        current_balance must be the employee's ACTUAL CURRENT
        REMAINING balance obtained from:

            get_leave_balance

        or:

            get_specific_leave_balance

        Do NOT use:
        - entitlement
        - used leave
        - a balance calculated by the LLM

        The calculation must use the actual database balance.
        """

        with ToolAuditContext(
            db,
            correlation_id=correlation_id,
            conversation_id=conversation_id,
            employee_id=employee_id,
            tool_name="calculate_remaining_leave",
        ):
            return LeaveCalculationTool.calculate_remaining_balance(
                current_balance,
                requested_days,
            )

    # =========================================================
    # 5. PL TO EL CONVERSION
    # =========================================================

    @tool
    def calculate_pl_to_el_conversion(
        pl_balance: int,
    ) -> dict[str, Any]:
        """
        Calculate PL to EL conversion according to the
        HR leave policy.

        The calculation is deterministic and must not be
        performed by the LLM.

        Example:

            PL = 13

            Retained PL = 7
            Converted PL = 6
            EL credited = 3
        """

        with ToolAuditContext(
            db,
            correlation_id=correlation_id,
            conversation_id=conversation_id,
            employee_id=employee_id,
            tool_name="calculate_pl_to_el_conversion",
        ):
            return PLConversionTool.calculate(
                pl_balance
            )

    # =========================================================
    # 6. CHECK LEAVE ELIGIBILITY
    # =========================================================

    @tool
    def check_leave_eligibility(
        leave_type: str,
        requested_days: float,
        current_balance: float,
    ) -> dict[str, Any]:
        """
        Check whether the requested leave can be taken based
        on the available leave balance.

        IMPORTANT:
        current_balance should come from the employee's actual
        database balance.

        Do not use entitlement as current balance.
        """

        with ToolAuditContext(
            db,
            correlation_id=correlation_id,
            conversation_id=conversation_id,
            employee_id=employee_id,
            tool_name="check_leave_eligibility",
        ):
            return LeaveEligibilityTool.check(
                leave_type,
                requested_days,
                current_balance,
            )

    # =========================================================
    # 7. SEARCH HR POLICY
    # =========================================================

    @tool
    def search_hr_policy(
        question: str,
    ) -> str:
        """
        Search the HR policy knowledge base.

        Use this tool for company HR policy questions such as:

        - leave entitlement
        - leave accrual
        - leave carry forward
        - leave encashment
        - maternity leave
        - paternity leave
        - adoption leave
        - leave application process
        - PL to EL conversion policy

        Do NOT use this tool for employee-specific balances.

        Employee-specific information must come from the
        authenticated HR database tools.
        """

        with ToolAuditContext(
            db,
            correlation_id=correlation_id,
            conversation_id=conversation_id,
            employee_id=employee_id,
            tool_name="search_hr_policy",
        ):
            return policy_search_tool.search(
                question
            )

    # =========================================================
    # RETURN ALL HR TOOLS
    # =========================================================

    return [
        get_employee_profile,
        get_leave_balance,
        get_specific_leave_balance,
        calculate_remaining_leave,
        calculate_pl_to_el_conversion,
        check_leave_eligibility,
        search_hr_policy,
    ]