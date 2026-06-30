# API Contract

Draft this fully in Phase 0 before writing component code — every other piece codes against this. Treat changes to this file after Phase 1 as a real decision, not a casual edit.

## Conventions

- All timestamps: ISO 8601 UTC
- All prices: integer ticks (avoid float for money — pick a tick size per instrument and document it)
- All IDs: ULID or UUID v7 (sortable by time — useful for ordering/debugging)

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

Response (202 Accepted):
```json
{
  "order_id": "string",
  "status": "accepted" | "rejected",
  "reject_reason": "string | null"
}
```

### `DELETE /orders/{order_id}`

Cancels an open order. Returns 200 with final status or 404 if not found/already filled.

## WebSocket: Market Data Feed

`GET /ws/marketdata?instrument=MOCK-USD` (upgrade, authenticated)

Server → client messages:

```json
// Order book delta
{
  "type": "book_update",
  "instrument": "MOCK-USD",
  "side": "buy",
  "price": 10050,
  "quantity": 200,
  "timestamp": "..."
}

// Trade event
{
  "type": "trade",
  "instrument": "MOCK-USD",
  "price": 10050,
  "quantity": 50,
  "timestamp": "...",
  "trade_id": "string"
}
```

## Internal: Engine → Gateway events (IPC)

Define the wire format here once you've picked the IPC mechanism (Phase 1). Likely a simple length-prefixed binary or JSON-lines protocol over a Unix socket — start with JSON-lines for development ease, consider binary later if you want a latency optimization story to tell.

```json
{"type": "order_ack", "order_id": "...", "timestamp": "..."}
{"type": "trade", "order_id": "...", "price": 10050, "quantity": 50, "timestamp": "..."}
{"type": "book_delta", "side": "buy", "price": 10050, "quantity": 200, "timestamp": "..."}
```

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
