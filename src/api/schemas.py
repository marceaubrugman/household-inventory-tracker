from pydantic import BaseModel


class ItemResponse(BaseModel):
    """Represent an inventory item returned by the API."""

    id: int
    name: str
    category: str
    quantity: int
    minimum_quantity: int
    location: str
    notes: str | None = None