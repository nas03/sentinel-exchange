# surveillance/ — Synthetic Order Flow, Detection, LLM Agent (Python)

## Scope

Three deliberately separate concerns:

```
surveillance/
├── bots/          # generates order flow against the live gateway — normal and manipulative
├── detectors/      # fast, deterministic rule-based flagging
└── llm_agent/      # explains flagged events in human-readable form
```

## Why rules come before the LLM

The rule-based detector runs on every event — cheap, deterministic, fast. It decides _what's worth looking at_. The LLM agent only runs on flagged events — it decides _how to explain what's already been flagged_. This split is itself a design decision worth defending in an interview: LLMs are the wrong tool for high-frequency deterministic triage, and the right tool for turning a flagged pattern into a readable explanation a human can act on.

## Build order (Roadmap Phase 4-5)

1. `bots/normal_trader.py` — baseline legitimate order flow (random walk around a reference price)
2. `bots/spoofer_bot.py`, `bots/layering_bot.py` — manipulative patterns, modeled on real enforcement case descriptions (see `docs/LEARNING-RESOURCES.md`)
3. `detectors/rule_based.py` — order-to-trade ratio, cancel rate, quote stuffing thresholds
4. `llm_agent/surveillance_agent.py` — structured input (flagged event + context) → structured explanation output

## Phase 6 extension (months out)

`llm_agent/adversary.py` — an agent that tries to craft order sequences that evade the rule-based detector, closing the loop into genuine adversarial AI red-teaming. This is the piece most directly relevant to your AI Red Teamer track — build it once the core detection loop is solid and trustworthy.

## Run

```bash
pip install -r requirements.txt
python -m bots.run_simulation
```
