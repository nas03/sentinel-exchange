"""Layering pattern: multiple orders at different price levels on one side
to create false depth, encouraging other participants to trade against the
illusion, then cancelling the layered orders.

TODO:
- place several orders at increasing distance from the touch, same side
- cancel the layer once a real trade occurs (the "real" goal order)
"""

from .base import TradingBot, OrderIntent


class LayeringBot(TradingBot):
    def __init__(self, instrument: str) -> None:
        self.instrument = instrument

    def next_action(self, market_state: dict) -> OrderIntent | None:
        # TODO: implement layering pattern
        raise NotImplementedError
