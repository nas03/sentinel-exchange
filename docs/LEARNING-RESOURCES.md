# Learning Resources

Organized by the phase that needs them. Don't read ahead of where you are — context from building makes these click better than reading cold.

## Phase 0-1: Matching engines & market microstructure

You likely have a head start here given `04-Resources/Market-Microstructure/` already exists in your vault — fold these in alongside it:
- Read about price-time priority and FIFO matching (any LOB primer)
- NASDAQ ITCH / OUCH protocol specs — real-world reference for how exchanges actually structure order/market-data messages
- "How to Build a Fast Limit Order Book" (search this exact phrase — there's a well-known WK Selph blog post that's a common reference point in this space)
- Unix domain sockets vs POSIX shared memory — Beej's Guide covers sockets well; for shared memory, look at ring buffer patterns used in low-latency systems

## Phase 1: Go concurrency & WebSockets

- Go's official "Effective Go" concurrency section
- `gorilla/websocket` or `nhooyr.io/websocket` docs and examples
- Pattern: one goroutine per WebSocket connection + a central broadcast hub — standard approach, look up "Go websocket hub pattern"

## Phase 2: Frontend real-time state

- React docs section on `useReducer` for complex state
- Pattern: separate "data layer" hooks from presentational components — look at how `react-use-websocket` or similar libraries structure reconnect logic, even if you write your own
- Recharts or D3 for the order book depth visualization

## Phase 3: Security

- OWASP API Security Top 10 (current version) — directly relevant to the gateway design
- STRIDE threat modeling — Microsoft's original methodology writeup is still the clearest intro
- Token bucket rate limiting algorithm
- JWT best practices — short expiry + refresh token rotation, why you don't store JWTs in localStorage

## Phase 4: Market manipulation patterns

- SEC and FCA publish real enforcement actions with detailed descriptions of spoofing/layering schemes — search "SEC spoofing enforcement order" for primary-source examples of what the behavior actually looks like in order flow
- "Quote stuffing" and "order-to-trade ratio" as detection signals — these terms will get you to the right academic/regulatory literature

## Phase 5: LLM agents for structured reasoning

- Anthropic's documentation on tool use and structured outputs (docs.claude.com) — directly applicable to the surveillance agent
- Prompt design for analytical tasks: the key shift from creative prompting is providing structured context (the flagged event + surrounding order book state) and asking for a structured, falsifiable explanation rather than free-form text
- This is also directly relevant to your AI Red Teamer study track — the adversarial agent in Phase 6 is genuinely the same skill set

## General: system design talking points

- "Designing Data-Intensive Applications" (Kleppmann) — not required reading cover to cover, but the chapters on replication and partitioning give you good language for the "how would you scale this" interview question
