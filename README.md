# Disruption Responder

A small multi-agent project for learning that reacts to supply-chain disruption events. When an event arrives (a supplier going down, a port closing, a demand spike, etc.), three lightweight "agents" cooperate to figure out how bad it is, what's at risk, and what to do about it. A markdown incident report is written for each event.

## How it works

```
events/*.json  ──►  Event Agent     (LLM, structured JSON)  ─► EventAssessment {severity, reason}
                ├─► Impact Agent    (compute_impact tool)   ─► [AffectedSku, ...]
                └─► Replan Agent    (LLM, structured JSON)  ─► ReplanPlan {actions, summary}
                                                 │
                                                 ▼
                                       incidents/incident_<date>_<event>.md
```

- **Event Agent** — calls the LLM with `with_structured_output(EventAssessment)`. Severity is a typed `Literal["LOW","MEDIUM","HIGH"]`.
- **Impact Agent** — pure Python; calls the `compute_impact` `@tool` against `world_state.json`. Returns a list of `AffectedSku` Pydantic models.
- **Replan Agent** — LLM with `with_structured_output(ReplanPlan)`. Returns a list of `SkuAction`s, each with `action ∈ {switch_supplier, expedite_shipping, raise_price}`.

All deterministic helpers (file IO, math, report writing) are exposed as LangChain `@tool`s in `disruption_responder/tools.py` so they can later be bound to an LLM if you want tool-calling agents.

## Project layout

```
disruption_responder/         # the framework package
├── __init__.py               # re-exports the Pydantic schemas
├── __main__.py               # `python -m disruption_responder`
├── cli.py                    # argv parsing + main()
├── config.py                 # loads .env, builds the shared ChatOpenAI client
├── orchestrator.py           # process_event(): glues the agents together
├── reporting.py              # markdown rendering + incident-path helpers
├── schemas.py                # EventAssessment, AffectedSku, SkuAction, ReplanPlan
├── tools.py                  # @tool: load_world_state, load_event, compute_impact, write_report
└── agents/
    ├── __init__.py
    ├── event_agent.py
    ├── impact_agent.py
    └── replan_agent.py
run.py                        # thin entrypoint -> disruption_responder.cli.main
world_state.json              # suppliers + SKUs (stock, sales, prices, backups)
events/                       # one JSON per disruption event
incidents/                    # generated markdown reports (one per event)
```

## Setup

Requires Python 3.13+.

```powershell
# create venv and install deps (uv or pip both work)
uv sync
# or:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

Create a `.env` file (it is gitignored):

```
# Pick one. LiteLLM is tried first, OpenAI as fallback.
LITELLM_API_KEY=sk-...
LITELLM_API_BASE=https://your-litellm-proxy/

# OR
OPENAI_API_KEY=sk-...
# OPENAI_BASE_URL=https://api.openai.com/v1   # optional

# Optional: override the model (default: gpt-5)
# DR_MODEL=gpt-4o-mini
```

## Usage

Three equivalent ways to run:

```powershell
# 1. via the run.py shim
python run.py

# 2. as a module
python -m disruption_responder

# 3. as a console script (after `pip install -e .`)
disruption-responder
```

Common invocations:

```powershell
# Process every NEW event in events/ (skips ones that already have a report today)
python run.py

# Re-process everything, even if a report already exists
python run.py --all

# Process specific event file(s) only
python run.py events/port_closure_typhoon.json
```

Reports are written to `incidents/incident_<YYYY_MM_DD>_<event-slug>.md`.

## Adding a new event

Drop a JSON file into `events/` following this shape:

```json
{
  "event_id": "EVT-2026-05-06-001",
  "headline": "Supplier B factory hit by power outage, shutdown expected for 14 days",
  "supplier_id": "supplier_b",
  "downtime_days": 14,
  "source": "supplier_email"
}
```

Then run `python run.py` — only the new event will be processed.

## Adding a new agent

1. Add a Pydantic schema for its output in `disruption_responder/schemas.py`.
2. Create `disruption_responder/agents/<name>_agent.py` with a function that uses `llm.with_structured_output(...)` (or a `@tool` from `tools.py`).
3. Re-export it from `disruption_responder/agents/__init__.py`.
4. Wire it into `disruption_responder/orchestrator.py:process_event`.

## Notes

- LLM calls go through `langchain-openai` (`ChatOpenAI`), so anything OpenAI-API-compatible (OpenAI, LiteLLM proxy, vLLM, etc.) works by setting `*_API_KEY` and `*_API_BASE`.
- Outputs are real JSON via Pydantic — no regex parsing.
- Never commit `.env`. If a key is ever exposed, rotate it immediately.
