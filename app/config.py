import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./hr.db",
    )

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "development-secret-change-me",
    )

    JWT_ALGORITHM = os.getenv(
        "JWT_ALGORITHM",
        "HS256",
    )

    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "60",
        )
    )

    OLLAMA_BASE_URL = os.getenv(
        "OLLAMA_BASE_URL",
        "http://127.0.0.1:11434",
    )

    OLLAMA_MODEL = os.getenv(
        "OLLAMA_MODEL",
        "llama3.2:3b",
    )


settings = Settings()