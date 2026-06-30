"""Takes a SurveillanceFlag (+ surrounding order book context) and produces
a structured, human-readable explanation — the kind a compliance analyst
could actually act on.

Build in Roadmap Phase 5, step 2. Read Anthropic's tool use / structured
output docs first (docs.claude.com) — the key design choice here is
requesting a structured response (e.g. a Pydantic-validated JSON shape:
summary, confidence, recommended_action) rather than free-form prose, so
the output is consistent and machine-checkable downstream.

Design note: this agent should NOT see the raw, unfiltered order stream —
only pre-filtered flags from detectors/rule_based.py. That's a deliberate
architectural boundary (see docs/01-ARCHITECTURE.md) worth being able to
explain: cost, latency, and determinism all favor keeping the LLM out of
the hot path.
"""

from dataclasses import dataclass

from detectors.rule_based import SurveillanceFlag


@dataclass
class SurveillanceReport:
    flag: SurveillanceFlag
    summary: str
    confidence: float
    recommended_action: str


def explain_flag(flag: SurveillanceFlag, order_book_context: dict) -> SurveillanceReport:
    """TODO: call the Anthropic API with the flag + context, parse a
    structured response into SurveillanceReport. Use a system prompt that
    frames this as an analytical task with a fixed output schema, not an
    open-ended chat.
    """
    raise NotImplementedError
