"""Orchestration: glue the agents together and persist the report."""

from .agents import event_agent, impact_agent, replan_agent
from .reporting import render_report_md, report_path_for
from .tools import load_event, write_report


def process_event(event_file: str, world: dict) -> None:
    print("\n" + "=" * 60)
    print(f"EVENT FILE: {event_file}")
    print("=" * 60)

    event = load_event.invoke({"path": event_file})
    print(f"\nNew event received: {event['headline']}")

    assessment = event_agent(event)
    affected = impact_agent(event, world)
    plan = replan_agent(affected, world)

    md = render_report_md(event, assessment.severity, affected, plan)
    path = write_report.invoke({"path": report_path_for(event_file), "content": md})
    print(f"\nReport saved to: {path}")
