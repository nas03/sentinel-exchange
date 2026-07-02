# Architecture

## Context and goals

Sentinel Exchange simulates a trading venue end to end: order matching, market data distribution, a trading UI, and a surveillance layer that detects manipulative behavior. The goal isn't just "a trading app" — it's a system that demonstrates three things an interviewer can probe independently:

1. **Performance engineering** — why the matching core is C++, what price-time priority means, where latency comes from and how you measured it
2. **Security architecture** — how you threat-modeled the system and what you did about each finding
3. **Applied AI** — using an LLM as a reasoning layer over structured data, not just a chatbot bolted onto the side

## Why polyglot (and not "just use TypeScript everywhere")

This is a deliberate choice — see `docs/adr/0002-polyglot-architecture.md` for the full reasoning. Short version: each language is doing the job it's actually good at, and being able to defend that choice in an interview is more valuable than a uniform stack.

- **C++** for the matching engine — predictable low-latency performance, manual memory control, the language real exchange cores are often written in
- **Go** for the gateway — strong concurrency primitives for handling many WebSocket connections, fast compile/iterate loop, good fit for a network-facing service layer
- **TypeScript/React** for the frontend — your strongest language, and the right tool for a real-time UI
- **Python** for the surveillance/AI layer — best ecosystem for LLM tooling, data manipulation, and rapid bot-behavior iteration

## Components

### `engine/` — Matching Engine (C++)

Owns the order book and matching logic exclusively. Responsibilities:

- Maintain price-time priority order book per instrument
- Process order add/cancel/modify
- Match orders, emit trade events
- Emit every order book change as an event (for market data + audit trail)

Does **not** handle auth, validation of business rules beyond order integrity, or networking beyond a local IPC boundary. Keep it focused — that boundary is itself a design decision worth documenting.

### `gateway/` — API Gateway (Go)

The only component exposed to the outside world. Responsibilities:

- Authentication (JWT) and authorization
- Input validation (reject malformed orders before they reach the engine)
- Rate limiting per client
- WebSocket fan-out of market data to many subscribers
- REST endpoints for order entry
- Audit logging of every action

This is where most of the security story lives. Structure internals by responsibility (`internal/auth`, `internal/orders`, `internal/marketdata`, `internal/ratelimit`) so each has a single clear job — that's the SOLID single-responsibility principle applied at the package level, and it's a clean thing to point to when asked about code organization.

### `frontend/` — Trading UI (TypeScript/React)

Responsibilities:

- Render live order book depth and trade tape from the WebSocket feed
- Order entry form with client-side validation
- Latency dashboard — this is a small addition that signals you understand what trading firms actually care about
- Auth flow

Keep components presentational where possible; push WebSocket connection management and message parsing into hooks/services so components stay easy to test (interface segregation — components depend only on the data shape they need, not the whole connection object).

### `surveillance/` — Bots + Detection + LLM Agent (Python)

A note on positioning: this layer is genuinely strong for _applied-AI_ and _fintech-compliance_ framing, but it's only loosely "cybersecurity" in the infosec sense. The parts of this project that actually speak to a cyber role (Orro etc.) are the gateway's threat model, secure-SDLC pipeline, auth, and rate limiting — not the trading surveillance. Frame accordingly depending on who you're talking to.

Three sub-responsibilities, deliberately separated:

- `bots/` — generates synthetic order flow, both legitimate and manipulative, against the live gateway
- `detectors/` — fast, deterministic rule-based detection (order-to-trade ratio, cancel rate, etc.)
- `llm_agent/` — takes events the rule-based layer flags and produces a structured, explainable report

The rule-based layer existing _before_ the LLM layer is itself a design decision worth defending: LLMs are slow and non-deterministic relative to threshold checks, so you use rules to cheaply triage and the LLM to explain — not to do the triage itself.

## Data flow

```
Order submitted (REST) → Gateway validates + authenticates → Engine matches
                                                                    │
                                                          order/trade events
                                                                    │
                                        ┌───────────────────────────┴───────────────────────────┐
                                        ▼                                                         ▼
                          Gateway → WebSocket → Frontend                          Surveillance: rule detector → (if flagged) LLM agent → report
```

## Key trade-offs to be ready to discuss

- IPC mechanism choice (Unix socket vs shared memory) between engine and gateway — start with a socket (simple, gets the slice working in days); treat shared memory as a _later, measured_ latency optimization with before/after numbers, not a starting point. The C++↔Go shared-memory path is a real multi-week detour for little early payoff.
- Why rate limiting lives in the gateway, not the engine
- Why the LLM agent only sees pre-filtered events, not the full order stream
- How you'd actually scale this past a single-process matching engine (you don't have to build this — but know the answer: sharding by instrument is the standard approach)

## Diagrams

Keep an up-to-date system diagram here as the project evolves — even a simple Excalidraw export committed to `docs/` is fine. Update it whenever a component's responsibility changes.
