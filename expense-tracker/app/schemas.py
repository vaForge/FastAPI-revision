# app/schemas.py
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


TransactionType = Literal["income", "expense"]


class TransactionCreate(BaseModel):
    """Validated input for creating a transaction."""

    title: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    transaction_type: TransactionType
    category: str = Field(min_length=1, max_length=100)
    transaction_date: date
    description: str | None = Field(default=None, max_length=2000)


class TransactionUpdate(BaseModel):
    """PATCH input: clients only need to supply fields they want to change."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    amount: Decimal | None = Field(
        default=None, gt=0, max_digits=12, decimal_places=2
    )
    transaction_type: TransactionType | None = None
    category: str | None = Field(default=None, min_length=1, max_length=100)
    transaction_date: date | None = None
    description: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def validate_patch(self):
        # Reject an empty PATCH and nulls for fields that must have values.
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update")

        required_fields = (
            "title", "amount", "transaction_type", "category", "transaction_date"
        )
        for field in required_fields:
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")

        return self


class TransactionResponse(BaseModel):
    """Public representation of a transaction returned by the API."""

    # Allow Pydantic to read values directly from SQLAlchemy model attributes.
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    amount: Decimal
    transaction_type: TransactionType
    category: str
    transaction_date: date
    description: str | None