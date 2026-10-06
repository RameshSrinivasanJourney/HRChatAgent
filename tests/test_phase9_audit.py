from app.agent.audit import record_audit_event
from app.database import SessionLocal
from app.models import AgentAuditLog


def test_audit_event_is_persisted():

    db = SessionLocal()

    try:
        record_audit_event(
            db,
            correlation_id="TEST-AUDIT-001",
            conversation_id="TEST-CONV-001",
            employee_id="EMP1001",
            event_type="TOOL_COMPLETED",
            status="SUCCESS",
            tool_name="get_leave_balance",
            duration_ms=12.34,
        )

        record = (
            db.query(AgentAuditLog)
            .filter(
                AgentAuditLog.correlation_id
                == "TEST-AUDIT-001"
            )
            .order_by(
                AgentAuditLog.id.desc()
            )
            .first()
        )

        assert record is not None
        assert record.employee_id == "EMP1001"
        assert record.conversation_id == "TEST-CONV-001"
        assert record.tool_name == "get_leave_balance"
        assert record.status == "SUCCESS"
        assert record.event_type == "TOOL_COMPLETED"

    finally:
        db.close()