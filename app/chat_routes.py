from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_employee
from app.models import Employee
from app.agent.service import HRChatService
from app.schemas import (
    CreateConversationResponse,
    ChatRequest,
    ChatResponse,
)
from app.logging_config import get_logger


logger = get_logger("hr_chat.chat")


router = APIRouter(
    prefix="/chat",
    tags=["HR Chat Agent"],
)


# =============================================================
# CREATE CONVERSATION
# =============================================================

@router.post(
    "/conversations",
    response_model=CreateConversationResponse,
)
def create_conversation(
    request: Request,
    current_employee: Employee = Depends(
        get_current_employee
    ),
    db: Session = Depends(get_db),
):

    correlation_id = getattr(
        request.state,
        "correlation_id",
        "unknown",
    )

    service = HRChatService(
        db,
        current_employee.employee_id,
        correlation_id,
    )

    conversation_id = service.create_conversation()

    logger.info(
        "conversation_created "
        "employee_id=%s "
        "conversation_id=%s "
        "correlation_id=%s",
        current_employee.employee_id,
        conversation_id,
        correlation_id,
    )

    return {
        "conversation_id": conversation_id
    }


# =============================================================
# CHAT
# =============================================================

@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: Request,
    chat_request: ChatRequest,
    current_employee: Employee = Depends(
        get_current_employee
    ),
    db: Session = Depends(get_db),
):

    correlation_id = getattr(
        request.state,
        "correlation_id",
        "unknown",
    )

    logger.info(
        "chat_request "
        "employee_id=%s "
        "conversation_id=%s "
        "correlation_id=%s",
        current_employee.employee_id,
        chat_request.conversation_id,
        correlation_id,
    )

    service = HRChatService(
        db,
        current_employee.employee_id,
        correlation_id,
    )

    try:

        response = service.chat(
            chat_request.conversation_id,
            chat_request.message,
        )

        logger.info(
            "chat_completed "
            "employee_id=%s "
            "conversation_id=%s "
            "correlation_id=%s",
            current_employee.employee_id,
            chat_request.conversation_id,
            correlation_id,
        )

        return {
            "conversation_id":
                chat_request.conversation_id,

            "employee_id":
                current_employee.employee_id,

            "message":
                response,
        }

    except ValueError as exc:

        logger.warning(
            "chat_validation_failed "
            "employee_id=%s "
            "conversation_id=%s "
            "correlation_id=%s "
            "error=%s",
            current_employee.employee_id,
            chat_request.conversation_id,
            correlation_id,
            str(exc),
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )

    except Exception:

        logger.exception(
            "chat_failed "
            "employee_id=%s "
            "conversation_id=%s "
            "correlation_id=%s",
            current_employee.employee_id,
            chat_request.conversation_id,
            correlation_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Unable to process HR chat request."
            ),
        )