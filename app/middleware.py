import time
import uuid

from fastapi import Request

from app.logging_config import get_logger


logger = get_logger("hr_chat.request")


async def correlation_id_middleware(
    request: Request,
    call_next,
):

    correlation_id = request.headers.get(
        "X-Correlation-ID"
    )

    if not correlation_id:
        correlation_id = str(uuid.uuid4())

    request.state.correlation_id = correlation_id

    start_time = time.perf_counter()

    logger.info(
        "request_started "
        "correlation_id=%s "
        "method=%s "
        "path=%s",
        correlation_id,
        request.method,
        request.url.path,
    )

    try:

        response = await call_next(request)

        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        response.headers[
            "X-Correlation-ID"
        ] = correlation_id

        logger.info(
            "request_completed "
            "correlation_id=%s "
            "status=%s "
            "duration_ms=%.2f",
            correlation_id,
            response.status_code,
            duration_ms,
        )

        return response

    except Exception:

        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.exception(
            "request_failed "
            "correlation_id=%s "
            "duration_ms=%.2f",
            correlation_id,
            duration_ms,
        )

        raise