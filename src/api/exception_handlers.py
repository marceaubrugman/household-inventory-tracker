import logging

import psycopg
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.database import DatabaseConfigurationError


logger = logging.getLogger(__name__)

DATABASE_UNAVAILABLE_DETAIL = "Database service is unavailable."


def _database_unavailable_response() -> JSONResponse:
    """Return the public response for unavailable database services."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": DATABASE_UNAVAILABLE_DETAIL},
    )


async def handle_database_configuration_error(
    _request: Request,
    _exception: DatabaseConfigurationError,
) -> JSONResponse:
    """Return a safe response when database configuration is missing."""
    return _database_unavailable_response()


async def handle_database_operational_error(
    _request: Request,
    exception: psycopg.OperationalError,
) -> JSONResponse:
    """Log database operational failures and return a safe response."""
    logger.error(
        "Database operation failed.",
        exc_info=(
            type(exception),
            exception,
            exception.__traceback__,
        ),
    )

    return _database_unavailable_response()


def register_exception_handlers(app: FastAPI) -> None:
    """Register application-wide API exception handlers."""
    app.add_exception_handler(
        DatabaseConfigurationError,
        handle_database_configuration_error,
    )
    app.add_exception_handler(
        psycopg.OperationalError,
        handle_database_operational_error,
    )