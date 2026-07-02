# Roadmap

> **Revision note (2026-07-02):** resequenced from the original breadth-first order. Engine Stage 2 + the honest benchmark moved up to **Phase 2** (immediately after the vertical slice) because the primary hiring audience is quant/trading firms and the engine is the protected deliverable. Security work is consolidated into a single-artifact phase (`docs/SECURITY.md`). The old Phases 2–6 are now Phases 3–7; content is otherwise preserved.

## Read this first: a realistic take on scope

The original version of this roadmap called this a "six-week core build." That was optimistic to the point of being misleading. Honestly: building a C++ matching engine from scratch, a Go gateway, a React frontend, a Python surveillance layer with an LLM agent, *and* a real security hardening pass is closer to **3-4 months at a sustainable part-time pace** — and you're starting at UTS in September, which eats into that.

That matters because the failure mode for ambitious portfolio projects is predictable: you build impressive-looking scaffolding across five areas, none of it quite connects end to end, and you end up with something that looks like a lot of work but doesn't actually *run* in a demo. For job-hunting, **a small thing that fully works beats a big thing that's half-built.** A recruiter who sees a 30-second video of orders matching live in a browser is more impressed than by a README describing a system that doesn't boot.

So the structure below is reorganized around one principle:

### Build a vertical slice before you build breadth

Get **one instrument trading end-to-end through every layer in the simplest possible form** before adding any sophistication. That means: submit one order → it matches in the engine → the trade shows up in the browser. No auth, no rate limiting, no bots, no LLM — just proof the whole pipe connects. Everything else is an enhancement on top of a thing that already works.

The "wow" layer is chosen and protected: **engine depth + the honest benchmark (Phase 2)**. If you finish the slice plus Phase 2 and nothing else, you already have the strongest version of this project for the primary audience — a working exchange pipe plus a measured, defensible matching-engine story. Security and AI extend that; they don't gate it. Don't let the later phases scope-creep into the core before the slice runs.

### Which layer maps to which audience (be deliberate)

- **Quant & trading firms — both trading-systems shops (Optiver, IMC, Jane Street) and SWE tracks at research shops (WorldQuant):** the *engine* is what they care about — correct matching semantics, property-tested invariants, real measured performance under real load, and a design you can defend. This holds for research shops' software-engineering roles too: those interviews probe CS fundamentals, C++/systems depth, and testing rigor, which is exactly what the engine + benchmark demonstrate. Depth in the core beats breadth of features. "I built a toy exchange" is common; "here's the p99 under 50k orders/sec and here's why it's that number" is not.
- **Cybersecurity (Orro etc.):** be honest with yourself — the *surveillance* layer is more applied-AI/fintech-compliance than infosec. The part that actually speaks to a cyber role is the **threat model, secure-SDLC pipeline (SAST/dep-scanning in CI), auth design, and rate limiting** — shipped as one artifact (`docs/SECURITY.md`, Phase 4). Lead with that framing when you talk to Orro, not the trading-surveillance angle.
- **AI/LLM skills:** the surveillance agent and (Phase 7) the adversarial evasion agent. This is the part most aligned with your AI Red Teamer track.

---

Each phase lists what to build, what to learn first, and a "done when" checkpoint. Don't skip the learning step — the point of this project is to be able to explain *why*, not just have it run.

**On timing:** the phases are *sequential*, not calendar-timed. Each takes as long as it takes — don't rush to a week number. As a whole, expect the core (Phases 0-6) to be 3-4 months part-time. Phase 0 is the only genuinely short one (~2-3 days). The two hard rules on ordering: **finish the vertical slice in Phase 1 before anything else, then go straight into Phase 2 (engine depth) before any polish.**

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
- [ ] Bare-minimum browser page that shows trades arriving (doesn't need to be pretty yet — that's Phase 3)

**On IPC — don't over-engineer this.** Use a Unix domain socket with a line-delimited JSON or simple length-prefixed format. I originally floated a shared-memory ring buffer as "more authentic," but C++↔Go shared memory means cgo, manual memory layout, and cross-language synchronization — it's a genuine multi-week rabbit hole that produces nothing demoable and is easy to get subtly wrong. A socket gets the slice working in days. If you later want a latency-optimization story for trading interviews, swapping the wire format to binary (or moving to shared memory) becomes a *deliberate, measured* enhancement with before/after numbers — which is a far better story than having started there. Record that swap as an ADR if you do it.

**Learn first:** Go's `gorilla/websocket` or `coder/websocket`; how real exchanges separate order-entry gateways from matching cores (see FIX/ITCH docs in `docs/LEARNING-RESOURCES.md` — read for *concepts*, don't implement the protocols yet)

**Done when:** you can submit an order via curl and watch the resulting trade appear in a browser tab in real time. This is your first demoable artifact — record a gif of it.

---

## Phase 2 — Engine depth + honest benchmark (the protected "wow" layer)

This comes **immediately after the slice, before any polish**. It's the deliverable that matters most to the primary audience, so it gets built while focus is highest — not deferred to last. This phase is engine M3 + M4 in `engine/BUILD-PLAN.md`.

**Build:**
- [ ] Benchmark Stage 1 (the map-based book) *first*, so the Stage 1 → Stage 2 delta is a measured result, not a claim
- [ ] Engine M3: port to Stage 2 — array-of-levels + object pool + intrusive lists. All existing invariant/golden/determinism tests must still pass unchanged; that's what they're for.
- [ ] Engine M4: the benchmark harness — drive the engine **in isolation** (directly over its socket, no gateway in the path) at a sustained, measured order rate; record p50/p99 order-to-event latency and max sustained throughput before latency degrades
- [ ] Microarchitecture analysis: identify the actual bottleneck (cache misses, branch mispredictions, allocation) with profiling data, not intuition
- [ ] Write it up — hardware, load profile, methodology, the bottleneck found, the fix, the delta — in `engine/bench/` or `docs/BENCHMARK.md`

**Benchmark environment (decide before starting M4):** macOS on Apple Silicon doesn't give you `perf`-style PMU counter access, and a non-pinned laptop core makes absolute numbers shaky. Plan to run the harness on a Linux box — a cheap bare cloud instance beats Docker-on-mac, where hardware counters are virtualized away — to get `perf stat` cache/branch data. Mac numbers are fine as a secondary datapoint; state the environment either way.

**Learn first:** cache hierarchy and locality of reference, why allocation in the hot path hurts (and how object pools fix it), intrusive vs node-based containers, benchmark methodology (warm-up, coordinated omission, percentiles vs averages), `perf stat` basics.

**Done when:** you have a written, reproducible before/after with an identified bottleneck — the "I measured X, found Y, changed Z, got W" story a trading interviewer can probe for twenty minutes without it collapsing.

---

## Phase 3 — Frontend polish

**Build:**
- [ ] `OrderBook` component — live bid/ask depth, updates from WebSocket
- [ ] `TradeTape` component — scrolling recent trades
- [ ] `OrderEntry` component — submit limit/market orders
- [ ] `useOrderBook` hook — reconnect logic, message parsing into typed events

**Learn first:** WebSocket reconnection strategies (exponential backoff), React state management for high-frequency updates (consider whether you need a state library or if `useReducer` + batching is enough — this is a good SOLID/architecture decision to document in an ADR)

**Done when:** you can watch the order book update live in the browser while submitting orders from a second tab.

---

## Phase 4 — Security hardening (ships as one artifact)

The cyber story ships as **one concentrated artifact**: a `docs/SECURITY.md` case study a security interviewer can walk through end to end. The items below are its *inputs* — build them, then write the case study that ties each threat → mitigation → validating test → residual risk.

**Build:**
- [ ] Fill in `docs/02-THREAT-MODEL.md` properly — STRIDE pass over the whole system (the template exists; the content is the work)
- [ ] Input validation layer in the gateway — reject malformed/out-of-bounds orders before they reach the engine
- [ ] Auth: JWT short-lived access + refresh tokens in the gateway; frontend auth flow (login → token → authenticated WebSocket connection)
- [ ] Rate limiting middleware in the gateway (token bucket per user/IP)
- [ ] Audit log — every order event written to an append-only log with actor, timestamp, action
- [ ] WebSocket-surface audit — what can an unauthenticated or malicious client do to `/ws/marketdata`? Connection exhaustion, slow-consumer handling, auth at upgrade. Test it, document it.
- [ ] Secure-SDLC in CI: Semgrep (or similar SAST), dependency scanning (`govulncheck`, `npm audit`, `pip-audit`), secret scanning
- [ ] Prove the pipeline: deliberately introduce a known-bad dependency or vulnerability, confirm CI fails, revert, keep the evidence
- [ ] Write `docs/SECURITY.md` — the case study that connects all of the above

**Learn first:** STRIDE methodology, token bucket vs sliding window rate limiting, JWT short-lived token + refresh pattern (and why tokens don't go in `localStorage`), OWASP API Security Top 10

**Done when:** `docs/SECURITY.md` exists and works as the single link you'd hand a security interviewer, and CI demonstrably fails on a known-bad dependency or a deliberately introduced vulnerability (with the evidence recorded).

---

## Phase 5 — Synthetic order flow

**Build:**
- [ ] `surveillance/bots/normal_trader.py` — random-walk style legitimate trading behavior
- [ ] `surveillance/bots/spoofer_bot.py` — places large orders away from the touch, cancels before fill
- [ ] `surveillance/bots/layering_bot.py` — multiple orders at different price levels to create false depth
- [ ] Bot orchestrator that runs a mix of normal + manipulative bots against the live engine

**Learn first:** what spoofing/layering/wash trading actually look like in order flow (read real enforcement cases — SEC/FCA publish these, they're great source material), order-to-trade ratio as a detection signal

**Done when:** you can run a simulation and visually tell, from the order book, that something's off — before you've written any detection code.

---

## Phase 6 — Detection + surveillance agent

**Build:**
- [ ] `surveillance/detectors/rule_based.py` — order-to-trade ratio, cancel rate, quote stuffing thresholds
- [ ] `surveillance/llm_agent/surveillance_agent.py` — takes flagged events + surrounding order book context, produces a structured human-readable report explaining *why* it looks manipulative
- [ ] Polish: architecture diagram, demo video/gif **at the top of the README** (recruiters give it ~20 seconds), repo description + topics carrying the searchable terms (matching engine, limit order book, low latency, market surveillance, LLM agent), full README pass

**Learn first:** structured output / tool use with LLM APIs, prompt design for analytical (not creative) tasks, why you still need rule-based pre-filtering before handing events to an LLM (cost, latency, determinism)

**Done when:** you can feed the agent a flagged event and get back a coherent explanation a compliance officer could actually use, and you have a public demo (video or hosted) ready to link from your CV/LinkedIn.

---

## Phase 7 — Extensions (months out, after the core ships)

These are the "keep going" items once Phases 0-6 are demoable. None of them should start before the core is complete.

- [ ] Adversarial agent that crafts order sequences to evade your own detectors — then harden detection in response (this is the "AI red teaming" showcase)
- [ ] FIX protocol support for order entry (realism + protocol-parsing experience)
- [ ] Backtesting module
- [ ] Simple LLM-driven trading agent using tool use to place strategic orders
- [ ] Deploy to AWS with least-privilege IAM, VPC, proper secrets management — write this up, it doubles as cloud/security evidence
- [ ] Open-source the repo properly, write a blog post walking through the architecture and design decisions (consider pulling a short benchmark-writeup post forward to when Phase 2 lands — it's the strongest single piece of content in the project)

---

## Notes on pacing

Phases 0-6 are the core — finishing them gives you a complete, demoable project worth putting on your CV, even if Phase 7 never ships. Within that, protect Phases 0-2 hardest: the slice plus engine depth is the centerpiece, and it must not lose focus to polish, security, or AI work. Don't let Phase 7 ideas (FIX protocol, AWS deploy, the adversarial agent) pull focus before the earlier phases are actually working. Ship the narrow version first.
