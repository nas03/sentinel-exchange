# Surveillance — Build Plan (Python)

Three deliberately separate concerns: generate order flow (bots), flag the suspicious stuff cheaply (detectors), explain the flags in human terms (LLM agent). The separation is itself a design argument you should be able to defend.

```
surveillance/
├── bots/          drives the gateway with normal + manipulative flow
├── detectors/      fast, deterministic rule-based flagging
└── llm_agent/      turns a flag into an explainable report
```

## How surveillance gets its data

Decide the tap point. Cleanest option: surveillance subscribes to the **same WebSocket market-data feed** the frontend uses, plus reads the gateway's **audit log** for the per-actor order/cancel detail it needs (the public feed may be anonymized). Document this — "what data does a surveillance system actually get to see" is a real design question and the answer affects what's detectable.

## Part 1 — Bots (Phase 4)

### `bots/base.py` — the interface (already scaffolded)
Every bot implements `next_action(market_state) -> OrderIntent | None`. This is open/closed: new manipulative patterns are new classes, the orchestrator never changes. Keep this interface small and stable.

### `bots/normal_trader.py` — build FIRST
You need a believable baseline before manipulation is interesting to detect. Random-walk around a reference price, post limit orders near the touch, occasional cancels, occasional crossing trades. Tune it so the book *looks* alive and healthy.

### `bots/spoofer_bot.py`
Places a large order several ticks from the touch (creating false pressure), cancels it before realistic fill, repeats — sometimes flipping the real trade to the opposite side. Model it on real enforcement-case descriptions (see `docs/LEARNING-RESOURCES.md`) so it's behaviorally realistic, not a caricature.

### `bots/layering_bot.py`
Multiple orders stacked at several price levels on one side to fake depth, cancelled once the genuine order on the other side fills.

### `bots/run_simulation.py` — orchestrator
Runs a *mixed population* (mostly normal, a few bad actors) against the live gateway on a tick loop. **Critical: log ground truth** — which bot placed which order. Without labels you can't measure whether your detector actually works, and the measurement is the whole point.

## Part 2 — Detectors (Phase 5, build before the LLM)

`detectors/rule_based.py` — deterministic metrics over sliding windows, per actor:
- **Order-to-trade ratio:** orders placed vs orders filled. Spoofers/layerers score high by construction.
- **Cancel rate / time-to-cancel:** fraction of orders cancelled within N ticks of placement.
- **Quote stuffing:** order submission rate per actor exceeding a threshold.

Each metric crossing a threshold emits a `SurveillanceFlag` (schema in `docs/03-API-CONTRACT.md`).

**Build an evaluation harness, not just the detector.** Run the labeled simulation, run the detector over it, compute **precision and recall** against the ground-truth labels. Tune thresholds against that. The deliverable line becomes: "catches X% of synthetic manipulation at Y% false-positive rate" — concrete, defensible, far stronger than "I wrote some detection rules."

Why rules before the LLM: they run on every event, cheaply and deterministically. They decide *what's worth a closer look*. The LLM never touches the high-frequency stream.

## Part 3 — LLM agent (Phase 5)

`llm_agent/surveillance_agent.py` — takes a `SurveillanceFlag` plus surrounding order-book context, returns a **structured** report (Pydantic-validated: `summary`, `confidence`, `recommended_action`), not free-form prose.

Design points (read Anthropic's tool-use / structured-output docs first):
- Frame the system prompt as an *analytical* task with a fixed output schema, not open-ended chat.
- Give it the flag + a window of surrounding events as structured context; ask for a falsifiable explanation tied to that evidence.
- Validate the response against the Pydantic schema; reject/retry on malformed output.
- **Architectural boundary:** the agent only ever sees pre-filtered flags, never the raw stream. Cost, latency, and determinism all favor keeping the LLM out of the hot path — be ready to explain exactly this.

## Part 4 — Adversary (Phase 6 / months later — the AI red-teaming showcase)

`llm_agent/adversary.py` — an agent that, given knowledge of your detection rules, tries to craft order sequences that achieve a manipulative goal *while staying under the thresholds*. Then you harden the detectors against what it finds, and iterate. This closed loop is genuine adversarial red-teaming and is the piece most aligned with your AI Red Teamer track. Build it only once the detection loop is solid and trustworthy — you can't measure evasion against a detector you don't trust.

## Testing & evaluation
- Bots: unit-test that each produces its intended *pattern* (e.g. the spoofer's cancel-before-fill ratio exceeds a bound).
- Detectors: the precision/recall harness above is the real test — keep its numbers in the repo.
- LLM agent: test schema validation and the pre-filter boundary with mocked API responses (don't burn tokens in CI). A small set of recorded flags → expected-shape reports.

## Milestones
1. **M1 (Phase 4):** normal trader + orchestrator producing a healthy-looking book against the live gateway, with ground-truth logging.
2. **M2 (Phase 4):** spoofer + layering bots mixed in — you should be able to *see* something's off in the UI before any detection code exists.
3. **M3 (Phase 5):** rule-based detector + evaluation harness with precision/recall numbers.
4. **M4 (Phase 5):** LLM surveillance agent producing structured reports.
5. **M5 (Phase 6):** adversarial agent + detector hardening loop.
