from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class ItemCreate(BaseModel):
    """Represent the data required to create an inventory item."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=0)
    minimum_quantity: int = Field(ge=0)
    location: str = Field(min_length=1, max_length=100)
    notes: str | None = Field(default=None, max_length=1000)


class ItemUpdate(BaseModel):
    """Represent fields that may be changed on an inventory item."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=100)
    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    quantity: int | None = Field(default=None, ge=0)
    minimum_quantity: int | None = Field(default=None, ge=0)
    location: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    notes: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_update_fields(self) -> Self:
        """Require at least one field and reject null required values."""
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")

        required_fields = {
            "name",
            "category",
            "quantity",
            "minimum_quantity",
            "location",
        }

        null_required_fields = required_fields.intersection(
            self.model_fields_set
        )

        for field_name in null_required_fields:
            if getattr(self, field_name) is None:
                raise ValueError(
                    f"{field_name} may not be null."
                )

        return self


class ItemResponse(BaseModel):
    """Represent an inventory item returned by the API."""

    id: int
    name: str
    category: str
    quantity: int
    minimum_quantity: int
    location: str
    notes: str | None = None