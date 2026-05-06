"""Deterministic helpers exposed as LangChain @tool's."""

import json
import os
from langchain_core.tools import tool


@tool
def load_world_state(path: str = "world_state.json") -> dict:
    """Load the world state JSON (suppliers + SKUs)."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@tool
def load_event(path: str) -> dict:
    """Load an event JSON file from disk."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@tool
def compute_impact(event: dict, world: dict) -> list[dict]:
    """Compute which SKUs are at risk given an event and the world state.

    Returns a list of dicts with sku_id, name, days_of_stock, will_stockout,
    revenue_at_risk, and backup_suppliers.
    """
    bad_supplier = event["supplier_id"]
    days_down = event["downtime_days"]

    out: list[dict] = []
    for sku_id, sku in world["skus"].items():
        if sku["primary_supplier"] != bad_supplier:
            continue

        days_left = sku["stock_units"] // max(sku["daily_sales"], 1)
        will_stockout = days_left < days_down

        revenue_at_risk = 0
        if will_stockout:
            missing_days = days_down - days_left
            revenue_at_risk = missing_days * sku["daily_sales"] * sku["unit_price"]

        out.append({
            "sku_id": sku_id,
            "name": sku["name"],
            "days_of_stock": int(days_left),
            "will_stockout": bool(will_stockout),
            "revenue_at_risk": float(revenue_at_risk),
            "backup_suppliers": sku["backup_suppliers"],
        })
    return out


@tool
def write_report(path: str, content: str) -> str:
    """Write the markdown report to disk and return the final path."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
