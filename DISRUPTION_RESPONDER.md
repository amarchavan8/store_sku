# Disruption Responder (Beginner Multi-Agent Project)

A small multi-agent demo for an **e-commerce supply chain**.

When a disruption event happens (e.g. a supplier goes offline), 3 agents
collaborate to respond in real time:

| Agent | What it does |
|---|---|
| **Event Agent** | Reads the event and tags severity (LOW / MEDIUM / HIGH) |
| **Impact Agent** | Figures out which products are at risk of stock-out |
| **Replan Agent** | Suggests a fix (switch supplier, expedite, raise price) |

## Why this project

- Real-world use case (every retailer deals with this).
- Only 3 agents → easy to understand.
- Mixes **LLM agents** with **plain Python logic** (the Impact Agent is just code — not every agent needs an LLM).
- Runs end-to-end with one command, no servers needed.

## Quickstart

```bash
pip install langchain langchain-openai python-dotenv
```

Add a `.env` file:

```
LITELLM_API_KEY=your-key-here
LITELLM_API_BASE=https://your-litellm-host/v1
# or just: OPENAI_API_KEY=sk-...
```

Then run:

```bash
python disruption_responder.py
```

## What you'll see

```
============================================================
DISRUPTION RESPONDER
============================================================

New event received: Supplier B factory hit by power outage...

[Event Agent] reading the event...
SEVERITY: HIGH
REASON: Two-week shutdown of a primary supplier with high-revenue SKUs.

[Impact Agent] checking which products are at risk...
  - Wireless Headphones      days_of_stock=  6  STOCK-OUT RISK  $ at risk=31,840
  - Laptop 14"               days_of_stock=  6  STOCK-OUT RISK  $ at risk=51,960
  - USB Mouse                days_of_stock= 20  ok              $ at risk=0

[Replan Agent] suggesting what to do...
- Headphones: switch to Supplier A immediately ...
- Laptop:     expedite from Supplier C ...

Report saved to: incident_2026_05_06.md
```

## File layout

```
disruption_responder.py        # the 3 agents + main loop
world_state.json               # SKUs, suppliers, inventory
events/
  supplier_b_shutdown.json     # one example event
DISRUPTION_RESPONDER.md        # this file
```

## How to extend (next steps)

1. Add more events in `events/` (demand spike, port closure, etc.).
2. Add a 4th **Negotiator Agent** that drafts emails to backup suppliers.
3. Read events from a folder in a loop → real-time mode.
4. Add a Streamlit dashboard.
5. Add an **LLM-as-judge** that scores how good each plan was.
