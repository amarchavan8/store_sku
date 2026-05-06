"""Event Agent: classifies severity. LLM-backed, returns Pydantic."""

import json
from ..config import llm
from ..schemas import EventAssessment


def event_agent(event: dict) -> EventAssessment:
    print("\n[Event Agent] reading the event...")

    structured_llm = llm.with_structured_output(EventAssessment)
    prompt = (
        "You are an Event Agent on a supply-chain team. "
        "Classify the severity of this disruption event as LOW, MEDIUM, or HIGH "
        "and give one short reason.\n\n"
        f"Event JSON:\n{json.dumps(event, indent=2)}"
    )
    result: EventAssessment = structured_llm.invoke(prompt)  # type: ignore[assignment]
    print(f"  severity={result.severity}  reason={result.reason}")
    return result
