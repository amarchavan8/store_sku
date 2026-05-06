# Disruption Responder (Beginner Multi-Agent Project)

A small multi-agent demo for an **e-commerce supply chain**.

When a disruption event happens (e.g. a supplier goes offline), 3 agents
collaborate to respond:

| Agent | Kind | What it does |
|---|---|---|
| **Event Agent**  | LLM (structured output) | Reads the event and returns `{severity: LOW/MEDIUM/HIGH, reason}` |
| **Impact Agent** | Pure Python tool        | Joins event vs. `world_state.json`; lists at-risk SKUs and revenue at risk |
| **Replan Agent** | LLM (structured output) | Returns one `SkuAction` per at-risk SKU (`switch_supplier`, `expedite_shipping`, `raise_price`) |

## Why this project

- Real-world use case (every retailer deals with this).
- Only 3 agents → easy to understand.
- Mixes **LLM agents** with **plain Python logic** (the Impact Agent doesn't need an LLM).
- Uses LangChain `@tool`s for deterministic work and Pydantic `with_structured_output(...)` for LLM agents — no string parsing.
- Runs end-to-end with one command, no servers needed.

## Quickstart

```powershell
pip install -e .
```

Create a `.env`:

```
LITELLM_API_KEY=your-key-here
LITELLM_API_BASE=https://your-litellm-host/v1
# or:
# OPENAI_API_KEY=sk-...
```

Then run:

```powershell
python run.py
# or:  python -m disruption_responder
# or:  disruption-responder
```

## What you'll see

```
============================================================
DISRUPTION RESPONDER
============================================================

EVENT FILE: events/supplier_b_shutdown.json

New event received: Supplier B factory hit by power outage...

[Event Agent] reading the event...
  severity=HIGH  reason=14-day shutdown likely causes major supply delays.

[Impact Agent] checking which products are at risk...
  - Wireless Headphones      days_of_stock=  6  STOCK-OUT RISK  $ at risk=31,840
  - Laptop 14"               days_of_stock=  6  STOCK-OUT RISK  $ at risk=51,960
  - USB Mouse                days_of_stock= 20  ok              $ at risk=0

[Replan Agent] suggesting what to do...
  - headphones: switch_supplier -> Switch to Supplier A (5d lead, +10% cost).
  - laptop:     expedite_shipping -> Air-freight to bridge 7d lead vs 6d stock.
  summary: Headphones: switch to Supplier A; Laptop: expedite shipping.

Report saved to: incidents\incident_2026_05_06_supplier_b_shutdown.md
```

## File layout

```
disruption_responder/        # framework package (config, schemas, tools, agents, ...)
run.py                       # thin entrypoint
world_state.json             # SKUs, suppliers, inventory
events/                      # one JSON per disruption event
incidents/                   # generated markdown reports
README.md                    # main docs
DISRUPTION_RESPONDER.md      # this file (project overview)
```

See [README.md](./README.md) for the full package layout, CLI usage, and how to add a new agent.

## How to extend (next steps)

1. Add more events in `events/` (demand spike, port closure, etc.).
2. Add a 4th **Negotiator Agent** that drafts emails to backup suppliers (new file in `disruption_responder/agents/`).
3. Read events from a folder in a loop → real-time mode.
4. Add a Streamlit dashboard.
5. Add an **LLM-as-judge** that scores how good each plan was.
6. Bind the `@tool`s to the LLM (`llm.bind_tools([...])`) so an agent can pick which tool to call.
