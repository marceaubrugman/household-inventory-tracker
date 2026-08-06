from fastapi import FastAPI, HTTPException

from src.api.exception_handlers import register_exception_handlers
from src.api.routers.items import router as items_router
from src.database import check_database_connection


app = FastAPI(
    title="Household Inventory Tracker API",
    version="0.6.0",
)

register_exception_handlers(app)
app.include_router(items_router)


@app.get(
    "/health",
    tags=["system"],
    summary="Check API liveness",
)
def get_health() -> dict[str, str]:
    """Return the API liveness status."""
    return {"status": "ok"}


@app.get("/db-health")
def db_health() -> dict:
    """Return database connection health information."""
    try:
        database_info = check_database_connection()
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        ) from error

    return {
        "status": "ok",
        "database": database_info,
    }