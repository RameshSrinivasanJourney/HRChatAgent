import time

from sqlalchemy.orm import Session

from app.logging_config import get_logger
from app.models import AgentAuditLog


logger = get_logger("hr_chat.audit")


def record_audit_event(
    db: Session,
    *,
    correlation_id: str,
    conversation_id: str | None,
    employee_id: str,
    event_type: str,
    status: str,
    tool_name: str | None = None,
    duration_ms: float | None = None,
    error_type: str | None = None,
):
    audit = AgentAuditLog(
        correlation_id=correlation_id,
        conversation_id=conversation_id,
        employee_id=employee_id,
        event_type=event_type,
        tool_name=tool_name,
        status=status,
        duration_ms=(
            f"{duration_ms:.2f}"
            if duration_ms is not None
            else None
        ),
        error_type=error_type,
    )

    db.add(audit)
    db.commit()

    logger.info(
        "audit_event "
        "event_type=%s "
        "employee_id=%s "
        "conversation_id=%s "
        "correlation_id=%s "
        "tool=%s "
        "status=%s "
        "duration_ms=%s "
        "error_type=%s",
        event_type,
        employee_id,
        conversation_id,
        correlation_id,
        tool_name,
        status,
        duration_ms,
        error_type,
    )


class ToolAuditContext:
    """
    Context manager used to audit tool execution.
    """

    def __init__(
        self,
        db: Session,
        *,
        correlation_id: str,
        conversation_id: str | None,
        employee_id: str,
        tool_name: str,
    ):
        self.db = db
        self.correlation_id = correlation_id
        self.conversation_id = conversation_id
        self.employee_id = employee_id
        self.tool_name = tool_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()

        record_audit_event(
            self.db,
            correlation_id=self.correlation_id,
            conversation_id=self.conversation_id,
            employee_id=self.employee_id,
            event_type="TOOL_STARTED",
            status="STARTED",
            tool_name=self.tool_name,
        )

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        duration_ms = (
            time.perf_counter() - self.start_time
        ) * 1000

        if exc_type is None:
            record_audit_event(
                self.db,
                correlation_id=self.correlation_id,
                conversation_id=self.conversation_id,
                employee_id=self.employee_id,
                event_type="TOOL_COMPLETED",
                status="SUCCESS",
                tool_name=self.tool_name,
                duration_ms=duration_ms,
            )

            return False

        record_audit_event(
            self.db,
            correlation_id=self.correlation_id,
            conversation_id=self.conversation_id,
            employee_id=self.employee_id,
            event_type="TOOL_FAILED",
            status="FAILED",
            tool_name=self.tool_name,
            duration_ms=duration_ms,
            error_type=type(exc_value).__name__,
        )

        return False