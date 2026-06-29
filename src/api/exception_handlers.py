from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.database import DatabaseConfigurationError


async def handle_database_configuration_error(
    _request: Request,
    _exception: DatabaseConfigurationError,
) -> JSONResponse:
    """Return a safe response when database configuration is unavailable."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Database service is unavailable."},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register application-wide API exception handlers."""
    app.add_exception_handler(
        DatabaseConfigurationError,
        handle_database_configuration_error,
    )