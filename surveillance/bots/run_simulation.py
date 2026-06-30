"""Orchestrator: runs a mixed population of bots against the live gateway.

TODO:
- instantiate a mix of NormalTraderBot, SpooferBot, LayeringBot
- on a fixed tick interval, ask each bot for its next_action()
- submit resulting OrderIntents to the gateway REST API (see docs/03-API-CONTRACT.md)
- log every submitted order with the bot's identity (needed later for
  evaluating detector accuracy against ground truth)
"""

if __name__ == "__main__":
    raise NotImplementedError("Implement orchestration loop — see module docstring")
