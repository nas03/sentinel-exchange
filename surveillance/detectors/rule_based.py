"""Deterministic, fast detection rules — run on every event, before any
LLM involvement. Decides WHAT gets escalated, not why it's suspicious
(that's the LLM agent's job).

Build in Roadmap Phase 5, step 1.

Metrics to implement (research each in docs/LEARNING-RESOURCES.md before
coding):
- order_to_trade_ratio: orders placed vs orders that actually fill, per
  actor per window. Spoofing/layering bots will have a high ratio by
  construction — validate your detector against the ground-truth bot
  labels from bots/run_simulation.py logs.
- cancel_rate: fraction of orders cancelled within N ticks of placement.
- quote_stuffing: order rate per actor per second exceeding a threshold.
"""

from dataclasses import dataclass


@dataclass
class SurveillanceFlag:
    """Matches the surveillance event schema in docs/03-API-CONTRACT.md."""
    flag_type: str
    actor_id: str
    instrument: str
    window_start: str
    window_end: str
    supporting_events: list[str]
    metric_value: float


def compute_order_to_trade_ratio(actor_id: str, events: list[dict]) -> float:
    """TODO: implement — orders placed / orders filled for this actor in the window."""
    raise NotImplementedError


def compute_cancel_rate(actor_id: str, events: list[dict]) -> float:
    """TODO: implement — fraction of orders cancelled within N ticks of placement."""
    raise NotImplementedError


def detect(events: list[dict]) -> list[SurveillanceFlag]:
    """TODO: run all metrics across actors in this window, return flags above threshold.

    Once implemented, validate against bots/run_simulation.py's ground-truth
    labels and record precision/recall in docs/ — this becomes a genuinely
    strong portfolio data point ("my detector catches X% of synthetic
    manipulative behavior with Y% false positive rate").
    """
    raise NotImplementedError
