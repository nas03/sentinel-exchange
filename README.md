# Sentinel Exchange

A simulated trading exchange with a self-policing surveillance layer: a high-performance matching engine, a security-hardened gateway, real-time market visualization, and an LLM agent that detects and explains manipulative trading behavior — with an adversarial AI layer that tries to evade its own detectors.

One system, three skill domains: low-latency systems engineering, applied security, and agentic AI.

## Why this exists

Built as a portfolio project to demonstrate depth across trading-systems engineering, security architecture, and applied AI — not three separate toy projects, but one coherent system where each layer depends on the others.

## Architecture at a glance

```
                    ┌─────────────────┐
                    │  React/TS UI    │  order book, trade tape,
                    │  (frontend/)    │  latency dashboard
                    └────────▲────────┘
                             │ WebSocket + REST
                    ┌────────┴────────┐
                    │   Go Gateway    │  auth, rate limiting,
                    │   (gateway/)    │  validation, audit log
                    └────────▲────────┘
                             │ IPC / shared memory
                    ┌────────┴────────┐
                    │  C++ LOB Engine │  order matching,
                    │   (engine/)     │  price-time priority
                    └────────▲────────┘
                             │ order/trade events
                    ┌────────┴────────┐
                    │  Surveillance   │  bot order flow generator,
                    │ (surveillance/) │  rule detector, LLM agent
                    └─────────────────┘
```

Full breakdown of responsibilities and data flow: [`docs/01-ARCHITECTURE.md`](docs/01-ARCHITECTURE.md)

## Quick start (once components are built)

```bash
# 1. Build and run the matching engine
cd engine && make && ./lob_engine

# 2. Run the gateway (connects to engine via IPC)
cd gateway && go run cmd/server/main.go

# 3. Run the frontend
cd frontend && npm install && npm run dev

# 4. Start synthetic order flow + surveillance
cd surveillance && pip install -r requirements.txt && python -m bots.run_simulation
```

## Repo map

| Path | Language | Purpose |
|---|---|---|
| `engine/` | C++ | Core matching engine — price-time priority order book, order add/cancel/match |
| `gateway/` | Go | API gateway — auth, validation, rate limiting, WebSocket fan-out, audit logging |
| `frontend/` | TypeScript/React | Live order book, trade tape, order entry, latency dashboard |
| `surveillance/` | Python | Synthetic trader bots, rule-based manipulation detection, LLM surveillance agent |
| `docs/` | Markdown | Roadmap, architecture decisions, threat model, API contract, learning resources |
| `infra/` | YAML | Local dev stack (docker-compose), CI config |

## Where to start — read in this order

You're not meant to read everything at once. Follow this path:

1. **This README** — you're here. Get the shape of the system from the diagram above.
2. **[`docs/00-ROADMAP.md`](docs/00-ROADMAP.md)** — the master plan. Phases 0-6, what to build in each, what to learn first, and a "done when" checkpoint for each. **This is your day-to-day driver.** Start at Phase 0 and don't skip ahead.
3. **[`docs/01-ARCHITECTURE.md`](docs/01-ARCHITECTURE.md)** — why the pieces are split the way they are, and the trade-offs to be ready to defend in interviews.
4. **[`docs/03-API-CONTRACT.md`](docs/03-API-CONTRACT.md)** — the messages every component agrees on. Settle this in Phase 0; everything codes against it.
5. **The component `BUILD-PLAN.md` for whatever you're currently building** — detailed design, milestones, and testing for that one component. Only open the one you need right now.

Reference docs you'll dip into as needed (not front-to-back reads):
- **[`docs/02-THREAT-MODEL.md`](docs/02-THREAT-MODEL.md)** — fill this in during Phase 3 (it's a template now).
- **[`docs/LEARNING-RESOURCES.md`](docs/LEARNING-RESOURCES.md)** — what to study, organized by the phase that needs it.
- **[`docs/adr/`](docs/adr/)** — architecture decision records. Read 0002 (why polyglot); add your own as you make calls.

### Doc map at a glance

| Doc | What it's for | When you read it |
|---|---|---|
| `docs/00-ROADMAP.md` | The plan, phase by phase | Constantly — it drives the work |
| `docs/01-ARCHITECTURE.md` | How/why the system is split | Once up front, revisit when a boundary changes |
| `docs/03-API-CONTRACT.md` | The shared message formats | Phase 0, then whenever the contract changes |
| `<component>/BUILD-PLAN.md` | Deep plan for one component | When you start building that component |
| `<component>/README.md` | Quick scope of one component | Quick orientation |
| `docs/02-THREAT-MODEL.md` | STRIDE security pass (template) | Phase 3 |
| `docs/LEARNING-RESOURCES.md` | Study material by phase | Before each phase's "learn first" step |
| `docs/adr/` | Why decisions were made | When deciding, or to recall reasoning |

### The one rule

Build the **vertical slice** (Phase 1) before anything else: one order matching end to end, engine → gateway → browser. It's the three milestones Engine M2 + Gateway M2 + Frontend M1. Nothing else starts until that runs.

## Status

🟡 Planning / scaffolding stage. All `BUILD-PLAN.md` files and stubs are in place; implementation not started. See the roadmap for the current phase.
