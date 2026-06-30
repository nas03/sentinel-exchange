"""Common interface for all trading bots.

Every bot (legitimate or manipulative) implements the same interface so
the orchestrator can run a mixed population without knowing which is
which — this is the open-closed principle in practice: adding a new bot
behavior later means adding a new class, not modifying the orchestrator.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class OrderIntent:
    """What a bot wants to do next — translated to a real API call by the orchestrator."""
    instrument: str
    side: str  # "buy" | "sell"
    order_type: str  # "limit" | "market"
    price: int
    quantity: int


class TradingBot(ABC):
    """Base class every bot extends. Keep this interface small and stable."""

    @abstractmethod
    def next_action(self, market_state: dict) -> OrderIntent | None:
        """Given current market state, decide the next order to place (or None to skip this tick)."""
        raise NotImplementedError
