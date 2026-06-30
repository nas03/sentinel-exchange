# ADR 0001: Record architecture decisions

## Status
Accepted

## Context
As this project grows, decisions get made (language choices, IPC mechanism, auth strategy) and the *reasoning* behind them is easy to forget — which is exactly the reasoning an interviewer will ask about. Writing it down as you decide, not retroactively, keeps it honest.

## Decision
Every non-trivial technical decision gets an ADR in `docs/adr/`, numbered sequentially. Use this format:

```
# ADR NNNN: <short title>

## Status
Proposed | Accepted | Superseded by ADR NNNN

## Context
What problem are you solving, what constraints matter.

## Decision
What you chose.

## Alternatives considered
What else you looked at and why you didn't pick it.

## Consequences
What this makes easier, what it makes harder, what you're trading off.
```

## Consequences
Slightly slower to make decisions (you have to write a paragraph). Much easier to explain the project in an interview, and much easier to revisit a decision later without re-deriving the reasoning from scratch.
