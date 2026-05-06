# Disruption Responder

A small multi-agent demo that reacts to supply-chain disruption events. When an event arrives (a supplier going down, a port closing, a demand spike, etc.), three lightweight "agents" cooperate to figure out how bad it is, what's at risk, and what to do about it. A markdown incident report is written for each event.

## How it works

```
events/*.json  ──►  Event Agent     (LLM)  ─► severity LOW / MEDIUM / HIGH
                ├─► Impact Agent    (pure Python) ─► at-risk SKUs + revenue
                └─► Replan Agent    (LLM)  ─► recommended action per SKU
                                                 │
                                                 ▼
                                       incidents/incident_<date>_<event>.md
```

- **Event Agent** — reads an event JSON and classifies its severity.
- **Impact Agent** — joins the event against `world_state.json` and computes which SKUs will stock out and the revenue at risk. No LLM needed.
- **Replan Agent** — for each at-risk SKU, suggests one concrete action (switch to a backup supplier, expedite, raise prices).

## Project layout

```
disruption_responder.py   # main script with the 3 agents
world_state.json          # suppliers + SKUs (stock, sales, prices, backups)
events/                   # one JSON per disruption event
incidents/                # generated markdown reports (one per event)
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
```

## Usage

```powershell
# Process every NEW event in events/ (skips ones that already have a report today)
python disruption_responder.py

# Re-process everything, even if a report already exists
python disruption_responder.py --all

# Process specific event file(s) only
python disruption_responder.py events/port_closure_typhoon.json
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

Then run `python disruption_responder.py` — only the new event will be processed.

## Notes

- This is a learning project: the "agents" are plain Python functions, not a framework.
- LLM calls go through `langchain-openai` (`ChatOpenAI`), so anything OpenAI-API-compatible (OpenAI, LiteLLM proxy, vLLM, etc.) works by setting `*_API_KEY` and `*_API_BASE`.
- Never commit `.env`. If a key is ever exposed, rotate it immediately.
