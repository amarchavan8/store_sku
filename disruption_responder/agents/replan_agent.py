"""Replan Agent: recommends one action per at-risk SKU. Returns Pydantic."""

import json
from ..config import llm
from ..schemas import AffectedSku, ReplanPlan


def replan_agent(affected: list[AffectedSku], world: dict) -> ReplanPlan:
    print("\n[Replan Agent] suggesting what to do...")

    at_risk = [a for a in affected if a.will_stockout]
    if not at_risk:
        print("  Nothing to replan - no stock-outs predicted.")
        return ReplanPlan(actions=[], summary="No action needed.")

    payload = {
        "at_risk_skus": [a.model_dump() for a in at_risk],
        "suppliers": world["suppliers"],
    }

    structured_llm = llm.with_structured_output(ReplanPlan)
    prompt = (
        "You are a Replan Agent. For each at-risk SKU, choose ONE action: "
        "switch_supplier (pick a specific backup), expedite_shipping, or raise_price. "
        "Use the supplier lead times and cost multipliers to make a sensible choice. "
        "Be concise.\n\n"
        f"Data:\n{json.dumps(payload, indent=2)}"
    )
    plan: ReplanPlan = structured_llm.invoke(prompt)  # type: ignore[assignment]

    for action in plan.actions:
        print(f"  - {action.sku_id}: {action.action} -> {action.detail}")
    print(f"  summary: {plan.summary}")
    return plan
