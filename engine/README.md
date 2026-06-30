# engine/ — Matching Engine (C++)

## Scope

A ground-up rebuild. The previous LOB project (`02-Projects/LOB-Engine`) is being abandoned — it had become hard to work with, and a clean build with the design decided up front will be stronger and more defensible than patching it. Keep the lessons from the old one, not the code.

See `engine/BUILD-PLAN.md` for the full design, the order-book data-structure decision, the matching rules, testing strategy, and milestones. Start there.

## What it needs for this project

- [ ] Correct price-time priority matching for one instrument (Stage 1: map-based)
- [ ] Event emission on every order book change — feeds market data, surveillance, and audit
- [ ] A Unix-socket IPC adapter (in `apps/`) so the gateway can drive it and read events back
- [ ] Clean separation: the `OrderBook` core owns matching only — no networking, no auth, no rate limiting

## Interface contract

See `docs/03-API-CONTRACT.md` for the exact event schema this component emits.

## Build

```bash
make        # or your existing build setup
./lob_engine
```

## Things to measure once running

- Order-to-ack latency (p50/p99) **under actual load** — measure while driving the engine at a sustained order rate, not with a single order in flight. Idle-system latency numbers are meaningless and a trading interviewer will know it.
- Throughput under synthetic load (orders/sec the engine can sustain before latency degrades)

Measure these honestly and write the methodology down — the load, the hardware, and especially the *bottleneck you hit and why*. "It plateaus at X orders/sec because of memory allocation in the hot path, which I then fixed by Y" is a genuinely strong talking point. A headline number with no methodology is a weak one.
