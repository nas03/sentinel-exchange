# API Contract

Draft this fully in Phase 0 before writing component code — every other piece codes against this. Treat changes to this file after Phase 1 as a real decision, not a casual edit.

## Conventions

- All timestamps: ISO 8601 UTC
- All prices: integer ticks (avoid float for money — pick a tick size per instrument and document it)
- All IDs: ULID or UUID v7 (sortable by time — useful for ordering/debugging)
- All market-data messages carry a monotonic per-instrument `seq` (engine-assigned logical time) so clients can order events and detect gaps

## REST: Order Entry

### `POST /orders`

Request:
```json
{
  "instrument": "MOCK-USD",
  "side": "buy" | "sell",
  "type": "limit" | "market",
  "price": 10050,
  "quantity": 100,
  "client_order_id": "string"
}
```

Response — `202 Accepted` (passed gateway validation and was forwarded to the engine; fills and book changes arrive asynchronously on the market-data feed — 202 means "accepted for processing," not "filled"):
```json
{
  "order_id": "string",
  "client_order_id": "string",
  "status": "accepted"
}
```

Response — `400 Bad Request` (failed gateway validation; the engine never saw it):
```json
{
  "client_order_id": "string",
  "reject_reason": "string"
}
```

### `DELETE /orders/{order_id}`

Cancels an open order. A cancel racing a fill is resolved by the engine's arrival order (`seq`) — the gateway reports whatever the engine decided:

- `200` with final status for any order the system knows about:
  ```json
  { "order_id": "string", "status": "cancelled" | "already_filled" | "already_cancelled" }
  ```
- `404` only for an `order_id` that never existed.

## WebSocket: Market Data Feed

`GET /ws/marketdata?instrument=MOCK-USD` (upgrade, authenticated)

Server → client messages:

```json
// Order book delta
{
  "type": "book_update",
  "instrument": "MOCK-USD",
  "seq": 1042,
  "side": "buy",
  "price": 10050,
  "quantity": 200,
  "timestamp": "..."
}

// Trade event
{
  "type": "trade",
  "instrument": "MOCK-USD",
  "seq": 1043,
  "price": 10050,
  "quantity": 50,
  "timestamp": "...",
  "trade_id": "string"
}
```

**Sequencing:** `seq` is monotonic per instrument, assigned by the engine. A client that observes a gap (`n` → `n+2`) has missed data and is desynced.

**Known v1 gap — no snapshot-on-subscribe.** A client that connects (or reconnects) mid-session starts from an empty book and cannot reconstruct resting depth from deltas alone. v1 accepts this deliberately: demo clients connect before order flow starts. The planned fix — documented here so it's a conscious gap, not an oversight — is a `book_snapshot` message sent on subscribe (which requires the gateway to maintain a live book cache off the engine feed), plus client resync-on-gap (v1 client behavior on a `seq` gap: clear book and reconnect). Build it when mid-session joins matter; record the design as an ADR then.

## Internal: Engine → Gateway events (IPC)

Define the wire format here once you've picked the IPC mechanism (Phase 1). Likely a simple length-prefixed binary or JSON-lines protocol over a Unix socket — start with JSON-lines for development ease, consider binary later if you want a latency optimization story to tell.

```json
{"type": "order_ack", "seq": 1041, "order_id": "...", "timestamp": "..."}
{"type": "trade", "seq": 1043, "order_id": "...", "price": 10050, "quantity": 50, "timestamp": "..."}
{"type": "book_delta", "seq": 1042, "side": "buy", "price": 10050, "quantity": 200, "timestamp": "..."}
```

`seq` is the engine's logical clock (arrival order — the same `Seq` that drives matching priority). Wall-clock timestamps are attached by the socket adapter in `engine/apps/`, never inside the matching core (see the determinism rules in `engine/BUILD-PLAN.md`).

## Internal: Surveillance event schema

What the rule-based detector hands to the LLM agent:

```json
{
  "flag_type": "high_cancel_rate" | "spoofing_pattern" | "layering_pattern",
  "actor_id": "string",
  "instrument": "MOCK-USD",
  "window_start": "...",
  "window_end": "...",
  "supporting_events": ["order_id", "..."],
  "metric_value": 0.0
}
```

## Auth

`POST /auth/login` → returns short-lived access token + refresh token. Document the exact expiry choices and why in `docs/02-THREAT-MODEL.md` once decided.

## Versioning

Treat this as v0 until Phase 1 is done and the contract is proven against real code — then tag it v1 and require an ADR for breaking changes.
