"""Baseline legitimate trading behavior: random walk around a reference price.

Build this FIRST (Roadmap Phase 4, step 1) — you need a believable "normal"
baseline before manipulative bots are interesting to detect against.

TODO:
- pick a reference price + volatility parameter
- on each tick, randomly decide buy/sell, price near reference +/- spread,
  reasonable quantity
- DO NOT cancel orders aggressively — that's what makes this "normal"
  versus the spoofer/layering bots
"""

from .base import TradingBot, OrderIntent


class NormalTraderBot(TradingBot):
    def __init__(self, instrument: str, reference_price: int) -> None:
        self.instrument = instrument
        self.reference_price = reference_price
        # TODO: volatility, spread, position tracking

    def next_action(self, market_state: dict) -> OrderIntent | None:
        # TODO: implement random-walk order generation
        raise NotImplementedError
