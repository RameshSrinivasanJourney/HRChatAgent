from pydantic import BaseModel


class LoginRequest(BaseModel):
    employee_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class EmployeeResponse(BaseModel):
    employee_id: str
    name: str
    email: str
    department: str
    role: str
    status: str


class LeaveBalanceResponse(BaseModel):
    employee_id: str
    leave_type: str
    entitlement: int
    used: int
    remaining: int


# ============================================================
# Phase 6 - Chat Schemas
# ============================================================

class CreateConversationResponse(BaseModel):
    conversation_id: str


class ChatRequest(BaseModel):
    conversation_id: str
    message: str


class ChatResponse(BaseModel):
    conversation_id: str
    employee_id: str
    message: str