from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings


ALGORITHM = settings.JWT_ALGORITHM

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    return pwd_context.verify(
        password,
        password_hash,
    )


def create_access_token(
    employee_id: str,
) -> str:

    expires = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": employee_id,
        "exp": expires,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> str:

    try:

        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        employee_id = payload.get("sub")

        if not employee_id:
            raise ValueError(
                "Invalid token"
            )

        return employee_id

    except (JWTError, ValueError):

        raise ValueError(
            "Invalid or expired token"
        )