from fastapi import FastAPI

from src.api.routers.items import router as items_router


app = FastAPI(
    title="Household Inventory Tracker API",
    version="0.3.0",
)

app.include_router(items_router)


@app.get(
    "/health",
    tags=["system"],
    summary="Check API liveness",
)
def get_health() -> dict[str, str]:
    """Return the API liveness status."""
    return {"status": "ok"}