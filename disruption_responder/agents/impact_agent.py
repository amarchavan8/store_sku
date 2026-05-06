"""Impact Agent: pure logic, calls the compute_impact tool."""

from ..schemas import AffectedSku
from ..tools import compute_impact


def impact_agent(event: dict, world: dict) -> list[AffectedSku]:
    print("\n[Impact Agent] checking which products are at risk...")
    raw = compute_impact.invoke({"event": event, "world": world})
    affected = [AffectedSku(**row) for row in raw]

    for a in affected:
        flag = "STOCK-OUT RISK" if a.will_stockout else "ok"
        print(
            f"  - {a.name:25s} days_of_stock={a.days_of_stock:>3}  "
            f"{flag}  $ at risk={a.revenue_at_risk:,.0f}"
        )
    return affected
