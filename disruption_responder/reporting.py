"""Markdown report rendering and incident-file path helpers."""

import os
from datetime import datetime
from .schemas import AffectedSku, ReplanPlan

REPORTS_DIR = "incidents"


def report_path_for(event_file: str) -> str:
    today = datetime.now().strftime("%Y_%m_%d")
    slug = os.path.splitext(os.path.basename(event_file))[0]
    return os.path.join(REPORTS_DIR, f"incident_{today}_{slug}.md")


def is_new_event(event_file: str) -> bool:
    """True if no report exists yet for this event today."""
    return not os.path.exists(report_path_for(event_file))


def render_report_md(event: dict, severity: str, affected: list[AffectedSku],
                     plan: ReplanPlan) -> str:
    today = datetime.now().strftime("%Y_%m_%d")
    lines = [
        f"# Incident Report - {today}",
        "",
        f"**Event:** {event['headline']}",
        "",
        f"**Severity:** {severity}",
        "",
        "## Affected Products",
        "",
    ]
    if not affected:
        lines += ["None.", ""]
    else:
        lines += [
            "| Product | Days of Stock | Stock-out? | Revenue at Risk |",
            "|---|---|---|---|",
        ]
        for a in affected:
            stockout = "YES" if a.will_stockout else "no"
            lines.append(
                f"| {a.name} | {a.days_of_stock} | {stockout} | ${a.revenue_at_risk:,.0f} |"
            )
        lines.append("")

    lines += ["## Recommended Plan", "", f"_Summary:_ {plan.summary}", ""]
    if plan.actions:
        for action in plan.actions:
            lines.append(f"- **{action.sku_id}** - `{action.action}` - {action.detail}")
    else:
        lines.append("- No action needed.")
    lines.append("")
    return "\n".join(lines)
