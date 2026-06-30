# frontend/ — Trading UI (TypeScript/React)

## Scope

Live order book, trade tape, order entry, and a latency dashboard. Auth flow against the gateway.

## Structure

```
frontend/src/
├── components/    # presentational — render props/state, no WebSocket logic
├── hooks/         # useWebSocket, useOrderBook, useAuth — stateful logic lives here
├── services/      # API client, WebSocket connection management
└── types/         # shared types mirroring docs/03-API-CONTRACT.md
```

## Design principle worth following deliberately

Keep `components/` dumb — they take typed props and render. All WebSocket connection handling, reconnection logic, and message parsing belongs in `hooks/` and `services/`. This is dependency inversion in practice: components depend on a typed data shape, not on *how* that data arrives. It also means you can test components with mock data and never spin up a WebSocket connection in a unit test.

## Build order (Roadmap Phase 2)

1. `types/` — mirror the API contract exactly, this is your source of truth
2. `services/websocket.ts` — connection + reconnect logic, emits typed events
3. `hooks/useOrderBook.ts` — subscribes to the service, maintains book state
4. `components/OrderBook.tsx`, `TradeTape.tsx` — presentational, consume the hooks
5. `components/OrderEntry.tsx` — form + submission via `services/api.ts`
6. Auth: `hooks/useAuth.ts` + protected routing

## Run

```bash
npm install
npm run dev
```
