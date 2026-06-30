# Roadmap

## Read this first: a realistic take on scope

The original version of this roadmap called this a "six-week core build." That was optimistic to the point of being misleading. Honestly: building a C++ matching engine from scratch, a Go gateway, a React frontend, a Python surveillance layer with an LLM agent, *and* a real security hardening pass is closer to **3-4 months at a sustainable part-time pace** — and you're starting at UTS in September, which eats into that.

That matters because the failure mode for ambitious portfolio projects is predictable: you build impressive-looking scaffolding across five areas, none of it quite connects end to end, and you end up with something that looks like a lot of work but doesn't actually *run* in a demo. For job-hunting, **a small thing that fully works beats a big thing that's half-built.** A recruiter who sees a 30-second video of orders matching live in a browser is more impressed than by a README describing a system that doesn't boot.

So the structure below is reorganized around one principle:

### Build a vertical slice before you build breadth

Get **one instrument trading end-to-end through every layer in the simplest possible form** before adding any sophistication. That means: submit one order → it matches in the engine → the trade shows up in the browser. No auth, no rate limiting, no bots, no LLM — just proof the whole pipe connects. Everything else is an enhancement on top of a thing that already works.

If you only ever finish the vertical slice plus *one* of the three "wow" layers (performance depth, security, or AI surveillance), you still have a strong, complete, demoable project. That's the safety net. Don't let the later phases scope-creep into the core before the slice runs.

### Which layer maps to which audience (be deliberate)

- **Trading firms (Optiver, Jane Street, IMC):** the *engine* is what they care about — correct matching semantics, real measured performance under real load, a clean design you can defend. Depth in the core beats breadth of features. "I built a toy exchange" is common; "here's the p99 under 50k orders/sec and here's why it's that number" is not.
- **Cybersecurity (Orro etc.):** be honest with yourself — the *surveillance* layer is more applied-AI/fintech-compliance than infosec. The part that actually speaks to a cyber role is the **threat model, secure-SDLC pipeline (SAST/dep-scanning in CI), auth design, and rate limiting**. Lead with that framing when you talk to Orro, not the trading-surveillance angle.
- **AI/LLM skills:** the surveillance agent and (phase 2) the adversarial evasion agent. This is the part most aligned with your AI Red Teamer track.

---

Each phase lists what to build, what to learn first, and a "done when" checkpoint. Don't skip the learning step — the point of this project is to be able to explain *why*, not just have it run.

**On timing:** the phases are *sequential*, not calendar-timed. Each takes as long as it takes — don't rush to a week number. As a whole, expect the core (Phases 0-5) to be 3-4 months part-time. Phase 0 is the only genuinely short one (~2-3 days). The single hard rule is ordering: **finish the vertical slice in Phase 1 before anything else.**

---

## Phase 0 — Before you write code (2-3 days)

- [ ] Read `docs/01-ARCHITECTURE.md` and sketch it in your own words on paper/Excalidraw
- [ ] Write `docs/03-API-CONTRACT.md` draft: every message your engine, gateway, frontend, and surveillance layer will exchange (order submit, cancel, ack, trade, market data tick). Get this stable before coding — it's the contract every component codes against.
- [ ] Skim the old `LOB-Engine` only to note what went wrong (what made it a mess) so the rebuild doesn't repeat it — then set it aside. The engine is a clean rebuild; see `engine/BUILD-PLAN.md`.

**Done when:** you have a one-page API contract and can draw the system from memory.

---

## Phase 1 — The vertical slice: engine ↔ gateway ↔ browser

This is the most important phase. Until this works, nothing else matters. Aim for the dumbest possible version of the whole pipe.

> **The slice = exactly these three milestones, in this order:**
> 1. **Engine M2** (`engine/BUILD-PLAN.md`) — runnable binary that matches orders and writes events to a Unix socket
> 2. **Gateway M2** (`gateway/BUILD-PLAN.md`) — forwards a submitted order to the engine, and broadcasts the engine's events back out over WebSocket
> 3. **Frontend M1** (`frontend/BUILD-PLAN.md`) — bare page that shows trades arriving
>
> Build them in that order. When all three are done, the slice is done. Nothing below this phase should start until they are.

**Build:**
- [ ] Build the C++ engine's runnable binary (see `engine/BUILD-PLAN.md` M1-M2) and have it emit order/trade events over a **Unix domain socket** (JSON-lines to start — one JSON object per line). See the IPC note below before reaching for anything fancier.
- [ ] Go gateway: connect to the engine socket, expose a WebSocket endpoint that streams market data ticks
- [ ] Go gateway: REST endpoint for order submission that forwards to the engine
- [ ] Bare-minimum browser page that shows trades arriving (doesn't need to be pretty yet — that's Phase 2)

**On IPC — don't over-engineer this.** Use a Unix domain socket with a line-delimited JSON or simple length-prefixed format. I originally floated a shared-memory ring buffer as "more authentic," but C++↔Go shared memory means cgo, manual memory layout, and cross-language synchronization — it's a genuine multi-week rabbit hole that produces nothing demoable and is easy to get subtly wrong. A socket gets the slice working in days. If you later want a latency-optimization story for trading interviews, swapping the wire format to binary (or moving to shared memory) becomes a *deliberate, measured* enhancement with before/after numbers — which is a far better story than having started there. Record that swap as an ADR if you do it.

**Learn first:** Go's `gorilla/websocket` or `coder/websocket`; how real exchanges separate order-entry gateways from matching cores (see FIX/ITCH docs in `docs/LEARNING-RESOURCES.md` — read for *concepts*, don't implement the protocols yet)

**Done when:** you can submit an order via curl and watch the resulting trade appear in a browser tab in real time. This is your first demoable artifact — record a gif of it.

---

## Phase 2 — Frontend polish

**Build:**
- [ ] `OrderBook` component — live bid/ask depth, updates from WebSocket
- [ ] `TradeTape` component — scrolling recent trades
- [ ] `OrderEntry` component — submit limit/market orders
- [ ] `useOrderBook` hook — reconnect logic, message parsing into typed events
- [ ] *Then, only after the above works:* basic JWT auth flow (login → token → authenticated WebSocket connection)

**Learn first:** WebSocket reconnection strategies (exponential backoff), React state management for high-frequency updates (consider whether you need a state library or if `useReducer` + batching is enough — this is a good SOLID/architecture decision to document in an ADR)

**Done when:** you can watch the order book update live in the browser while submitting orders from a second tab.

---

## Phase 3 — Security hardening

**Build:**
- [ ] Write `docs/02-THREAT-MODEL.md` properly — STRIDE pass over the whole system
- [ ] Rate limiting middleware in the gateway (token bucket per user/IP)
- [ ] Input validation layer — reject malformed/out-of-bounds orders before they reach the engine
- [ ] Audit log — every order event written to an append-only log with actor, timestamp, action
- [ ] Add Semgrep (or similar SAST) to CI; fix or consciously accept findings
- [ ] Dependency scanning (`govulncheck`, `npm audit`, `pip-audit`)

**Learn first:** STRIDE methodology, token bucket vs sliding window rate limiting, JWT short-lived token + refresh pattern, OWASP API Security Top 10

**Done when:** you have a threat model doc you could walk a security interviewer through, and CI fails on a known-bad dependency or a deliberately introduced vulnerability (test this).

---

## Phase 4 — Synthetic order flow

**Build:**
- [ ] `surveillance/bots/normal_trader.py` — random-walk style legitimate trading behavior
- [ ] `surveillance/bots/spoofer_bot.py` — places large orders away from the touch, cancels before fill
- [ ] `surveillance/bots/layering_bot.py` — multiple orders at different price levels to create false depth
- [ ] Bot orchestrator that runs a mix of normal + manipulative bots against the live engine

**Learn first:** what spoofing/layering/wash trading actually look like in order flow (read real enforcement cases — SEC/FCA publish these, they're great source material), order-to-trade ratio as a detection signal

**Done when:** you can run a simulation and visually tell, from the order book, that something's off — before you've written any detection code.

---

## Phase 5 — Detection + honest benchmark

**Build:**
- [ ] `surveillance/detectors/rule_based.py` — order-to-trade ratio, cancel rate, quote stuffing thresholds
- [ ] `surveillance/llm_agent/surveillance_agent.py` — takes flagged events + surrounding order book context, produces a structured human-readable report explaining *why* it looks manipulative
- [ ] Latency *benchmark* (not just a dashboard): a proper load test that drives the engine at a measured order rate and records p50/p99 order-to-ack and matching latency. **Be honest about methodology** — a dashboard showing single-digit-microsecond latency on an idle system with one order in flight is meaningless, and a trading interviewer will see through it instantly. The value is in the rigor: state the load, the hardware, the measurement method, and the *bottleneck you found*. "Throughput plateaus at ~X orders/sec because of [specific reason]" is a real engineering story; a pretty Grafana panel with no load behind it is not.
- [ ] Polish: architecture diagram, demo video/gif, full README pass

**Learn first:** structured output / tool use with LLM APIs, prompt design for analytical (not creative) tasks, why you still need rule-based pre-filtering before handing events to an LLM (cost, latency, determinism)

**Done when:** you can feed the agent a flagged event and get back a coherent explanation a compliance officer could actually use, and you have a public demo (video or hosted) ready to link from your CV/LinkedIn.

---

## Phase 6 — Extensions (months out, after the core ships)

These are the "keep going" items once Phases 0-5 are demoable. None of them should start before the core is complete.

- [ ] Adversarial agent that crafts order sequences to evade your own detectors — then harden detection in response (this is the "AI red teaming" showcase)
- [ ] FIX protocol support for order entry (realism + protocol-parsing experience)
- [ ] Backtesting module
- [ ] Simple LLM-driven trading agent using tool use to place strategic orders
- [ ] Deploy to AWS with least-privilege IAM, VPC, proper secrets management — write this up, it doubles as cloud/security evidence
- [ ] Open-source the repo properly, write a blog post walking through the architecture and design decisions

---

## Notes on pacing

Phases 0-5 are the core — finishing them gives you a complete, demoable project worth putting on your CV, even if Phase 6 never ships. Protect that core: don't let Phase 6 ideas (FIX protocol, AWS deploy, the adversarial agent) pull focus before the slice and at least one "wow" layer are actually working. Ship the narrow version first.
