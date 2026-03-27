from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class Product(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    sku: str
    name: str
    profit_margin: float

    @field_validator("profit_margin")
    @classmethod
    def margin_must_be_valid(cls, v: float) -> float:
        if v < 0 or v >= 100:
            raise ValueError("profit_margin must be >= 0 and < 100")
        return v


class Material(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    product_sku: str
    name: str
    unit_cost: float
    quantity: float

    @field_validator("unit_cost")
    @classmethod
    def unit_cost_must_be_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("unit_cost must be >= 0")
        return v

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("quantity must be > 0")
        return v


class Labor(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    product_sku: str
    hours: float
    hourly_rate: float

    @field_validator("hours", "hourly_rate")
    @classmethod
    def must_be_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("value must be >= 0")
        return v


class Overhead(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    product_sku: str
    rent: float
    tools: float
    packaging: float
    shipping: float
    taxes: float

    @field_validator("rent", "tools", "packaging", "shipping", "taxes")
    @classmethod
    def must_be_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("value must be >= 0")
        return v


class PriceBreakdown(BaseModel):
    product_name: str
    materials_subtotal: float
    labor_subtotal: float
    overhead_subtotal: float
    rent: float
    tools: float
    packaging: float
    shipping: float
    taxes: float
    total_cost: float
    profit_margin: float
    selling_price: float
