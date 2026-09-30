import os

from dotenv import load_dotenv


# Load environment variables from the project's .env file.
# This does NOT modify or delete any database.
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "farm-management-secret-key",
    )

    # Supabase PostgreSQL is used when DATABASE_URL exists.
    # If DATABASE_URL is unavailable, the existing local SQLite
    # database remains the fallback.
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgres://",
                "postgresql://",
                1,
            )

        if DATABASE_URL.startswith("postgresql://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgresql://",
                "postgresql+psycopg://",
                1,
            )

        SQLALCHEMY_DATABASE_URI = DATABASE_URL

    else:
        DATABASE_PATH = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "instance",
            "farm.db",
        )

        SQLALCHEMY_DATABASE_URI = "sqlite:///" + DATABASE_PATH

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    FARM_NOTIFICATION_EMAIL = os.environ.get("FARM_NOTIFICATION_EMAIL")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME")

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    OPENAI_MODEL = os.environ.get(
        "OPENAI_MODEL",
        "gpt-5.6-luna",
    )