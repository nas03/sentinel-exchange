"""Spoofing pattern: place large orders away from the touch to create a
false impression of supply/demand, then cancel before they'd ever fill.

Research real enforcement case descriptions before implementing (see
docs/LEARNING-RESOURCES.md) — the goal is a behaviorally realistic
pattern, not a caricature.

TODO:
- place a large order several ticks away from the best bid/ask
- cancel it after N ticks (well before realistic fill probability)
- repeat, optionally alternating sides
"""

from .base import TradingBot, OrderIntent


class SpooferBot(TradingBot):
    def __init__(self, instrument: str) -> None:
        self.instrument = instrument
        # TODO: track open spoof orders for cancellation timing

    def next_action(self, market_state: dict) -> OrderIntent | None:
        # TODO: implement spoof placement/cancellation cycle
        raise NotImplementedError
