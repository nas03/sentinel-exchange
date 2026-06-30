# Gateway — Build Plan (Go)

The only network-facing component. Owns everything between the outside world and the engine: auth, validation, rate limiting, WebSocket fan-out, audit logging. This is where most of your *security* story lives.

## Design goals

- One clear responsibility per package (single-responsibility at the package level)
- Engine core stays untrusted-input-free: the gateway validates everything before forwarding
- Many concurrent WebSocket subscribers, fanned out from one engine event stream
- Every action audit-logged; every client rate-limited
- Testable without the engine running (mock the engine connection)

## Concurrency model (decide this first)

Go's strength here. The model:
- **One goroutine per client connection** (read pump + write pump per WebSocket client).
- **A central `Hub`** owns the set of connected clients. Clients are registered/unregistered via channels — the Hub goroutine is the *only* thing that touches the client map, so there's no shared-mutable-state to lock. This is the idiomatic Go approach; look up the "gorilla websocket hub" example for the canonical shape.
- **Backpressure:** each client has a buffered send channel. If a slow client's buffer fills, you drop the client rather than blocking the Hub — a slow consumer must never stall market data for everyone else. Decide and document the policy (disconnect-on-full is the standard, simplest correct choice).

## Package-by-package plan

```
gateway/
├── cmd/server/main.go      # wiring only — no logic
└── internal/
    ├── engineclient/        # NEW: owns the Unix-socket connection to the engine
    ├── marketdata/          # WebSocket Hub + client pumps, fan-out
    ├── orders/              # REST order submit/cancel, validation
    ├── auth/                # JWT issue/verify, middleware
    ├── ratelimit/           # token bucket middleware
    └── audit/               # NEW: append-only structured event log
```

(Two packages added vs the original scaffold: `engineclient` so the socket connection has one owner shared by `orders` and `marketdata`, and `audit` so logging isn't smeared across every handler.)

### `engineclient` — build first
- Dials the engine's Unix socket, handles reconnect with backoff if the engine restarts.
- Exposes two things: a way to *send* an order to the engine, and a *channel of events* coming back.
- Framing: read line-delimited JSON to start (matches the engine's JSON-lines output). Keep the framing logic in one place so a later switch to a binary format touches only this package.
- **Interface (so everything else can be tested against a mock):**
  ```go
  type EngineClient interface {
      SubmitOrder(ctx context.Context, o Order) error
      Events() <-chan Event   // book deltas, trades, acks
  }
  ```

### `marketdata` — build second (completes the slice)
- `Hub` struct: `clients map[*Client]bool`, `register`/`unregister`/`broadcast` channels, a `Run()` loop.
- Consumes `engineclient.Events()`, marshals each into the wire format from `docs/03-API-CONTRACT.md`, broadcasts to all subscribed clients.
- `ServeWS(w, r)`: upgrades to WebSocket, creates a `Client`, registers it, starts its read/write pumps.

### `orders` — build third
- `POST /orders`: decode → validate (see below) → `engineclient.SubmitOrder` → return ack/reject.
- `DELETE /orders/{id}`: cancel path.
- **Validation is message-integrity only:** correct types, side ∈ {buy,sell}, type ∈ {limit,market}, price > 0 and within tick bounds, quantity > 0 and within limits, required fields present. NOT business logic like balance checks (out of scope — document it). Reject malformed input here so the engine never sees it.

### `auth` — Phase 3 (after the slice works)
- `POST /auth/login`: verify credentials → issue short-lived access token (minutes) + refresh token.
- Middleware: verify the bearer token on protected routes, attach the user identity to the request context. The WebSocket upgrade is also gated by this.
- Decisions to record in `docs/02-THREAT-MODEL.md`: token expiry values, refresh rotation, why tokens don't go in `localStorage`.

### `ratelimit` — Phase 3
- Token bucket per authenticated client (per IP for unauthenticated endpoints).
- Middleware wrapping the order handlers. Inject the clock as an interface so you can test refill behavior without sleeping.
- **Test it for real:** drive orders faster than the bucket refills, assert rejection after the threshold; record the test + result in the threat model's validation section.

### `audit` — Phase 3
- Append-only, structured (JSON lines) log of every order event: actor, action, order details, timestamp, sequence. This is your Repudiation mitigation in STRIDE.
- Keep the writer behind an interface; for v1 a file is fine, note that production would want tamper-evidence (hash chaining / WORM storage) — saying that in the writeup shows you know the gap.

## main.go — wiring, in order

```
load config →
dial engineclient (with reconnect) →
start marketdata.Hub.Run() in a goroutine, fed by engineclient.Events() →
register /ws/marketdata (marketdata.ServeWS) and /orders (orders handlers) →
[Phase 3] wrap protected routes with auth + ratelimit middleware, attach audit →
start HTTP server
```

If logic creeps into `main.go`, it belongs in a package.

## Config & observability
- Config via env vars (engine socket path, listen port, JWT secret, token TTLs). Never hardcode secrets; read `JWT_SECRET` from the environment, document it in the README.
- Structured logging (`slog`) from day one.
- A `/metrics` endpoint (Prometheus) once you reach the benchmark phase — order counts, WebSocket connection gauge, latency histograms.

## Testing
- `engineclient`: test framing/reconnect against a fake socket server.
- `orders`: table-driven validation tests with a mock `EngineClient`.
- `marketdata`: test the Hub register/unregister/broadcast logic and the slow-client drop policy with fake clients.
- `ratelimit`: deterministic tests with an injected clock.
- If a package is hard to test in isolation, that's a signal it's doing too much.

## Milestones
1. **M1:** `engineclient` connects to the engine, surfaces events. (Depends on engine M2.)
2. **M2 (completes the slice):** `marketdata` Hub broadcasts engine events over WebSocket, **and** a minimal `orders` `POST /orders` that forwards a well-formed order straight to the engine (no validation, no auth yet). Together with engine M2 and frontend M1, this is the end-to-end vertical slice: curl an order in, see the trade in the browser.
3. **M3 (Phase 3):** harden the `orders` path — real input validation, reject malformed/out-of-bounds orders before the engine sees them; add `DELETE /orders/{id}`.
4. **M4 (Phase 3):** `auth`, `ratelimit`, `audit` + the threat-model validation tests.
