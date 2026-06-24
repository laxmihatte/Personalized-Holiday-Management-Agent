# Personalized Holiday Management Agent

> A multi-agent travel-planning service. Two AI agents — a **Planner** and a
> **Researcher** — collaborate to draft a day-by-day itinerary from a single
> sentence, and the system **remembers each traveller's preferences** across
> visits to personalize future plans.

![CI](https://github.com/<your-username>/Personalized-Holiday-Management-Agent/actions/workflows/ci.yml/badge.svg)

---

## What it does

You describe a trip in plain English ("Plan a 5-day budget trip to Paris for a
family that loves art"). Behind a FastAPI endpoint, an [AutoGen](https://microsoft.github.io/autogen/)
agent team runs a round-robin conversation:

1. **Holiday Planner** structures the trip into days and sequences attractions.
2. **Holiday Researcher** enriches the plan with opening hours, local tips, and
   food recommendations. It **calls a live weather tool** (Open-Meteo) for the
   destination and adapts the plan to the forecast — indoor activities on rainy
   days — then signals completion.

Requests are validated and normalized, every step is logged, and the
traveller's stated preferences are stored in a vector memory ([mem0](https://github.com/mem0ai/mem0)
+ Chroma) so the next plan is automatically personalized.

## Architecture

```
                         ┌──────────────────────────────┐
   Browser (Jinja2 UI)   │            FastAPI            │
        │  POST /plan ───▶│                              │
        │                 │  1. Validate + normalize     │  query_processing
        │                 │  2. Recall preferences ──────┼──▶ mem0 + Chroma (./db)
        │                 │  3. Run agent team           │
        │                 │  4. Remember request ────────┼──▶ mem0 + Chroma
        │   itinerary ◀───│  5. Return PlanResponse      │
                          └───────────────┬──────────────┘
                                          │
                          ┌───────────────▼──────────────┐
                          │   AutoGen RoundRobinGroupChat │
                          │   Planner  ⇄  Researcher      │  (OpenAI gpt-4o-mini)
                          └──────────────────────────────┘
```

| Layer | Tech | Responsibility |
|-------|------|----------------|
| API | FastAPI, Pydantic | Typed `/plan` + `/health`, request validation, structured responses |
| Agents | AutoGen, OpenAI | Planner + Researcher round-robin with termination conditions |
| Tools | Open-Meteo (no key) | Researcher calls a live weather tool to ground the plan (indoor activities on rainy days) |
| Memory | mem0, Chroma | Per-traveller preference store for personalization |
| Cross-cutting | logging, query normalization | Observability + input hygiene |
| Frontend | Jinja2, vanilla JS/CSS | Timeline view of the generated itinerary |
| Quality | pytest, ruff, GitHub Actions | Hermetic tests (no API key needed) + CI |

## Quickstart

### Option A — Docker (one command)

```bash
cp .env.example .env          # add your OPENAI_API_KEY
docker compose up --build
```
Open http://localhost:8000

### Option B — Local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add your OPENAI_API_KEY
uvicorn app:app --reload
```

## API

`POST /plan`
```json
{ "content": "Plan a 5-day budget trip to Paris for a family", "user_id": "laxmi" }
```
Returns a typed `PlanResponse` with the agent conversation, a request
`signature`, and any `remembered` preferences applied. Interactive docs at
`/docs`. Health check at `/health`.

## Testing

The suite is **hermetic** — the heavy LLM stack is stubbed, so tests run with no
API key and no network:

```bash
pip install -r requirements-test.txt
pytest
```

CI runs lint + tests on Python 3.11 and 3.12 (see `.github/workflows/ci.yml`).

## Project layout

```
app.py                         FastAPI app: endpoints + request pipeline
holiday_management/
  agents/      planner.py, researcher.py     AutoGen assistant agents
  teams/       holiday_team.py               round-robin team assembly
  models/      gpt_model.py, schemas.py      OpenAI client + Pydantic schemas
  memory/      holiday_memory.py             mem0 preference store (graceful)
  utils/       logging_config.py, query_processing.py
  config/      settings.py
templates/ static/                           Jinja2 UI
tests/                                        pytest suite + hermetic conftest
```

## Notes

- Memory is **best-effort**: if mem0/Chroma is unavailable the request still
  succeeds; the failure is logged and personalization is skipped.
- Default model is `gpt-4o-mini` (configurable in `holiday_management/config/settings.py`).
