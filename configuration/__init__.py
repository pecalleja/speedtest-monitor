import logging
import os


class BaseConfig:
    """
    FLASK configuration

    Please be sure to add your .env file to your project
    All envs marked with default are optional
    """

    ENV = FLASK_ENV = ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
    if "test" in ENV.lower():
        TESTING = True
    else:
        TESTING = False

    # Debug flag and default logger level
    if os.getenv("DEBUG", "").lower() in ["yes", "true", "1"]:
        DEBUG = FLASK_DEBUG = True
    else:
        DEBUG = FLASK_DEBUG = False

    LEVEL = logging.DEBUG if DEBUG else logging.INFO

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URI", "sqlite:///speedtest.db")
    SQLALCHEMY_DB_SCHEMA = os.getenv("DB_SCHEMA", default="public")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # YOUR STUFF
    TIMEZONE = os.getenv("TIMEZONE", "America/Mexico_City")
    COMMAND = ["speedtest", "--format=json"]
    SPEEDFACTOR = float(
        os.getenv("SPEEDFACTOR", default="125.000696706770313")
    )
