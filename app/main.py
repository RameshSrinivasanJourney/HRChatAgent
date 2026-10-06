from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import Base, engine
from app.logging_config import configure_logging
from app.middleware import correlation_id_middleware

from app.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler,
)

from app.auth_routes import router as auth_router
from app.chat_routes import router as chat_router
from app.employee_routes import router as employee_router
from app.leave_routes import router as leave_router


configure_logging()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HR Chat Agent",
    version="1.0.0",
)


app.middleware("http")(correlation_id_middleware)


app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    Exception,
    global_exception_handler,
)


app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(employee_router)
app.include_router(leave_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "hr-chat-agent",
    }