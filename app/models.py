from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    department = Column(String, nullable=False)
    role = Column(String, nullable=False)
    status = Column(String, nullable=False, default="ACTIVE")
    password_hash = Column(String, nullable=False)

    leave_balances = relationship(
        "LeaveBalance",
        back_populates="employee",
        cascade="all, delete-orphan"
    )


class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(
        String,
        ForeignKey("employees.employee_id"),
        nullable=False,
        index=True
    )
    leave_type = Column(String, nullable=False)
    entitlement = Column(Integer, nullable=False)
    used = Column(Integer, nullable=False, default=0)
    remaining = Column(Integer, nullable=False)

    employee = relationship("Employee", back_populates="leave_balances")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String, unique=True, nullable=False, index=True)
    employee_id = Column(
        String,
        ForeignKey("employees.employee_id"),
        nullable=False,
        index=True,
    )


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(
        String,
        ForeignKey("conversations.conversation_id"),
        nullable=False,
        index=True,
    )
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)

class AgentAuditLog(Base):
    __tablename__ = "agent_audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    correlation_id = Column(
        String,
        nullable=False,
        index=True,
    )

    conversation_id = Column(
        String,
        nullable=True,
        index=True,
    )

    employee_id = Column(
        String,
        nullable=False,
        index=True,
    )

    event_type = Column(
        String,
        nullable=False,
        index=True,
    )

    tool_name = Column(
        String,
        nullable=True,
    )

    status = Column(
        String,
        nullable=False,
    )

    duration_ms = Column(
        String,
        nullable=True,
    )

    error_type = Column(
        String,
        nullable=True,
    )
