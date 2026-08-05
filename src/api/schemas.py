from typing import Literal, Self

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
    location: str = Field(min_length=1, max_length=100)
    tracking_mode: Literal[
        "quantity",
        "individual",
    ] = "quantity"
    quantity: int | None = Field(default=None, ge=0)
    minimum_quantity: int | None = Field(
        default=None,
        ge=0,
    )
    notes: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_tracking_mode_fields(self) -> Self:
        """Require quantity fields to match the tracking mode."""
        if self.tracking_mode == "quantity":
            if (
                self.quantity is None
                or self.minimum_quantity is None
            ):
                raise ValueError(
                    "Quantity-tracked items require quantity "
                    "and minimum_quantity."
                )

        if self.tracking_mode == "individual":
            if (
                self.quantity is not None
                or self.minimum_quantity is not None
            ):
                raise ValueError(
                    "Individual items may not have quantity "
                    "or minimum_quantity."
                )

        return self


class ItemUpdate(BaseModel):
    """Represent fields that may be changed on an inventory item."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=100)
    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    location: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    tracking_mode: Literal[
        "quantity",
        "individual",
    ] | None = None
    quantity: int | None = Field(default=None, ge=0)
    minimum_quantity: int | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_update_fields(self) -> Self:
        """Validate partial updates and tracking-mode transitions."""
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")

        non_nullable_fields = {
            "name",
            "category",
            "location",
            "tracking_mode",
        }

        supplied_non_nullable_fields = (
            non_nullable_fields.intersection(
                self.model_fields_set
            )
        )

        for field_name in supplied_non_nullable_fields:
            if getattr(self, field_name) is None:
                raise ValueError(
                    f"{field_name} may not be null."
                )

        tracking_mode_supplied = (
                "tracking_mode" in self.model_fields_set
        )
        quantity_supplied = (
                "quantity" in self.model_fields_set
        )
        minimum_quantity_supplied = (
                "minimum_quantity" in self.model_fields_set
        )

        tracking_mode_supplied = (
            "tracking_mode" in self.model_fields_set
        )
        quantity_supplied = (
            "quantity" in self.model_fields_set
        )
        minimum_quantity_supplied = (
            "minimum_quantity" in self.model_fields_set
        )

        if tracking_mode_supplied:
            if not (
                quantity_supplied
                and minimum_quantity_supplied
            ):
                raise ValueError(
                    "Changing tracking_mode requires quantity "
                    "and minimum_quantity."
                )

            if self.tracking_mode == "quantity":
                if (
                    self.quantity is None
                    or self.minimum_quantity is None
                ):
                    raise ValueError(
                        "Quantity-tracked items require quantity "
                        "and minimum_quantity."
                    )

            if self.tracking_mode == "individual":
                if (
                    self.quantity is not None
                    or self.minimum_quantity is not None
                ):
                    raise ValueError(
                        "Individual items may not have quantity "
                        "or minimum_quantity."
                    )

        else:
            nullable_quantity_fields = {
                "quantity",
                "minimum_quantity",
            }.intersection(self.model_fields_set)

            for field_name in nullable_quantity_fields:
                if getattr(self, field_name) is None:
                    raise ValueError(
                        f"{field_name} may not be null unless "
                        "tracking_mode is changed."
                    )

        return self


class ItemResponse(BaseModel):
    """Represent an inventory item returned by the API."""

    id: int
    name: str
    category: str
    location: str
    tracking_mode: Literal["quantity", "individual"]
    quantity: int | None
    minimum_quantity: int | None
    notes: str | None = None
