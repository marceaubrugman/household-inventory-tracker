from pydantic import BaseModel, ConfigDict, Field


class ItemCreate(BaseModel):
    """Represent the data required to create an inventory item."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=0)
    minimum_quantity: int = Field(ge=0)
    location: str = Field(min_length=1, max_length=100)
    notes: str | None = Field(default=None, max_length=1000)


class ItemResponse(BaseModel):
    """Represent an inventory item returned by the API."""

    id: int
    name: str
    category: str
    quantity: int
    minimum_quantity: int
    location: str
    notes: str | None = None