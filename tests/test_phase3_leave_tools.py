import pytest

from app.tools.leave_tools import (
    LeaveCalculationTool,
    PLConversionTool,
    LeaveEligibilityTool,
)


# --------------------------------------------------
# Leave Balance Calculation
# --------------------------------------------------

def test_leave_calculation_success():

    result = (
        LeaveCalculationTool
        .calculate_remaining_balance(
            current_balance=8,
            requested_days=3,
        )
    )

    assert result["eligible"] is True
    assert result["remaining_balance"] == 5


def test_leave_calculation_insufficient_balance():

    result = (
        LeaveCalculationTool
        .calculate_remaining_balance(
            current_balance=3,
            requested_days=5,
        )
    )

    assert result["eligible"] is False
    assert result["remaining_balance"] == 3


def test_leave_calculation_invalid_request():

    with pytest.raises(ValueError):

        LeaveCalculationTool \
            .calculate_remaining_balance(
                current_balance=8,
                requested_days=0,
            )


# --------------------------------------------------
# PL Conversion
# --------------------------------------------------

def test_pl_conversion_six_days():

    result = (
        PLConversionTool.calculate(6)
    )

    assert result["retained_pl"] == 6
    assert result["el_credit"] == 0
    assert result["conversion_applied"] is False


def test_pl_conversion_ten_days():

    result = (
        PLConversionTool.calculate(10)
    )

    assert result["retained_pl"] == 6
    assert result["converted_pl"] == 4
    assert result["el_credit"] == 2


def test_pl_conversion_eleven_days():

    result = (
        PLConversionTool.calculate(11)
    )

    assert result["retained_pl"] == 7
    assert result["converted_pl"] == 4
    assert result["el_credit"] == 2


def test_pl_conversion_thirteen_days():

    result = (
        PLConversionTool.calculate(13)
    )

    assert result["retained_pl"] == 7
    assert result["converted_pl"] == 6
    assert result["el_credit"] == 3


# --------------------------------------------------
# Leave Eligibility
# --------------------------------------------------

def test_leave_eligibility_success():

    result = (
        LeaveEligibilityTool.check(
            leave_type="CL",
            requested_days=3,
            current_balance=8,
        )
    )

    assert result["eligible"] is True
    assert result["remaining_balance"] == 5


def test_leave_eligibility_insufficient_balance():

    result = (
        LeaveEligibilityTool.check(
            leave_type="EL",
            requested_days=10,
            current_balance=5,
        )
    )

    assert result["eligible"] is False


def test_leave_eligibility_invalid_leave_type():

    result = (
        LeaveEligibilityTool.check(
            leave_type="XYZ",
            requested_days=2,
            current_balance=10,
        )
    )

    assert result["eligible"] is False