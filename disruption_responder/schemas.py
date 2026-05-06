"""Pydantic schemas: the JSON shapes our agents speak."""

from typing import Literal
from pydantic import BaseModel, Field


class EventAssessment(BaseModel):
    """What the Event Agent returns."""
    severity: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        description="How serious the disruption is."
    )
    reason: str = Field(description="One short sentence explaining why.")


class AffectedSku(BaseModel):
    sku_id: str
    name: str
    days_of_stock: int
    will_stockout: bool
    revenue_at_risk: float
    backup_suppliers: list[str]


class SkuAction(BaseModel):
    sku_id: str
    action: Literal["switch_supplier", "expedite_shipping", "raise_price"]
    detail: str = Field(description="Specific recommendation, e.g. 'switch to Supplier C'.")


class ReplanPlan(BaseModel):
    """What the Replan Agent returns."""
    actions: list[SkuAction]
    summary: str = Field(description="One-line summary of the overall plan.")
