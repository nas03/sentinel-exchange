# gateway/ — API Gateway (Go)

## Scope

The only network-facing component. Owns auth, validation, rate limiting, WebSocket fan-out, and audit logging. Forwards validated orders to the engine over IPC and relays engine events back out.

## Package layout

```
gateway/
├── cmd/server/main.go      # entry point, wiring
└── internal/
    ├── auth/                # JWT issuance/verification, login handler
    ├── orders/               # order submission/cancel handlers, validation
    ├── marketdata/           # WebSocket hub, broadcast to subscribers
    └── ratelimit/            # token bucket middleware
```

Each package has one job — this is single-responsibility applied at the package level. If you find yourself importing `orders` from inside `ratelimit`, that's a sign something's misplaced.

## Build order (matches Roadmap Phase 1 & 3)

1. `internal/marketdata` — connect to engine IPC, broadcast over WebSocket (get data flowing first)
2. `internal/orders` — REST order submission, forward to engine
3. `internal/auth` — JWT login, middleware to protect order/WebSocket endpoints
4. `internal/ratelimit` — token bucket middleware, applied per authenticated client

## Run

```bash
go run cmd/server/main.go
```

## Testing approach

Each `internal/` package should be testable without the other three running — mock the engine IPC connection for `orders` and `marketdata` tests, mock the clock for `ratelimit` tests. If a package is hard to test in isolation, that's usually a signal it's taking on more than one responsibility.
