import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.logging_config import get_logger


logger = get_logger("hr_chat.exception")


def get_correlation_id(request: Request) -> str:
    return getattr(
        request.state,
        "correlation_id",
        "unknown",
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    correlation_id = get_correlation_id(request)

    logger.warning(
        "http_exception "
        "correlation_id=%s "
        "status=%s "
        "path=%s "
        "detail=%s",
        correlation_id,
        exc.status_code,
        request.url.path,
        exc.detail,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": str(exc.detail),
            "correlation_id": correlation_id,
        },
        headers={
            "X-Correlation-ID": correlation_id,
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    correlation_id = get_correlation_id(request)

    logger.warning(
        "request_validation_failed "
        "correlation_id=%s "
        "path=%s "
        "errors=%s",
        correlation_id,
        request.url.path,
        exc.errors(),
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": "Invalid request data",
            "correlation_id": correlation_id,
        },
        headers={
            "X-Correlation-ID": correlation_id,
        },
    )


async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    correlation_id = get_correlation_id(request)

    logger.exception(
        "unhandled_exception "
        "correlation_id=%s "
        "method=%s "
        "path=%s",
        correlation_id,
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "correlation_id": correlation_id,
        },
        headers={
            "X-Correlation-ID": correlation_id,
        },
    )
