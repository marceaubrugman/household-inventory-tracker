from fastapi import FastAPI


app = FastAPI(
    title="Household Inventory Tracker API",
    version="0.3.0",
)


@app.get(
    "/health",
    tags=["system"],
    summary="Check API liveness",
)
def get_health() -> dict[str, str]:
    """Return the API liveness status."""
    return {"status": "ok"}