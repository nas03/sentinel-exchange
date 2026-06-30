# Frontend — Build Plan (TypeScript / React)

A real-time trading UI: live order book, trade tape, order entry, and a latency panel. The interesting engineering here is **handling a high-frequency update stream without melting React's render loop** — that's the part worth getting right and talking about.

## Architecture (layered, SOLID)

```
types/       ← source of truth, mirrors docs/03-API-CONTRACT.md
   ↑
services/    ← talks to the network. WebSocket + REST. The ONLY layer that knows about transport.
   ↑
hooks/       ← stateful logic. Subscribes to services, maintains derived state.
   ↑
components/  ← presentational. Take typed props, render. No transport, no business logic.
```

The rule: a component never imports from `services/` directly and never touches a raw WebSocket. It consumes a hook. This is dependency inversion in practice — components depend on a *data shape*, not on how the data arrives — and it means every component is unit-testable with mock props and zero network.

## The hard part: high-frequency updates

The order book can update many times per second. Naively calling `setState` on every tick will re-render constantly and tank performance. Strategy:

- Keep the authoritative book state in a `useReducer` or a `useRef`, mutated on each incoming message **without** triggering a render per message.
- **Batch renders with `requestAnimationFrame`:** accumulate updates, flush to React state at most once per animation frame (~60fps). The user can't perceive faster than that anyway.
- Memoize the order book rows (`React.memo`) so only changed price levels re-render.
- Decide this consciously and write it up as an ADR — "how I handle a high-frequency feed in React" is a genuinely good frontend interview topic, and the wrong-but-simple version (setState per tick) is a good thing to show you rejected.

This is also a good place to ask whether you even need a state library. For one feed into a few components, `useReducer` + rAF batching is enough; reaching for Redux/Zustand here would be over-engineering. Document that you considered it.

## Build order (Phase 2, after the slice's bare page exists)

1. **`types/api.ts`** — already written; keep it the single source of truth. Update it first if the contract changes and let TS errors guide the rest.
2. **`services/websocket.ts`** — `MarketDataSocket` class: connect, parse incoming JSON into the `MarketDataMessage` discriminated union, emit to subscribers, reconnect with exponential backoff on close/error. This is the only place `new WebSocket()` appears.
3. **`services/api.ts`** — REST client for order submit/cancel and auth. Typed request/response against the contract.
4. **`hooks/useOrderBook.ts`** — subscribes to `MarketDataSocket`, maintains book state with the rAF-batching approach above, returns `{ bids, asks, isConnected }`.
5. **`hooks/useTradeTape.ts`** — maintains a capped list of recent trades.
6. **`components/OrderBook.tsx`** — renders bid/ask depth from the hook. Consider a depth-bar visual (colored background width ∝ cumulative volume) — cheap to build, looks impressive in a demo.
7. **`components/TradeTape.tsx`** — scrolling recent trades.
8. **`components/OrderEntry.tsx`** — controlled form (NO `<form>` submit; use `onClick` handlers), client-side validation mirroring the gateway's, calls `services/api.ts`, surfaces accept/reject.
9. **Phase 3:** `hooks/useAuth.ts` + an `AuthGate` wrapper for protected views; attach the token to the WebSocket connection and REST calls.
10. **`components/LatencyPanel.tsx`** — once the engine exposes timing, show p50/p99. Keep it honest — label it as measured-under-load, not idle.

## Component design rules

- Presentational components take data + callbacks as props, nothing else.
- Container logic (which hook, which instrument) lives one layer up.
- Interface segregation: a component's props should be the *minimum* shape it needs — `OrderBook` takes `bids`/`asks`, not the whole socket or the whole app state.

## Tooling
- Vite (already in `package.json`), TypeScript strict mode on.
- Testing: Vitest + React Testing Library. Test components with mock props; test hooks with a fake `MarketDataSocket`. No real WebSocket in unit tests.
- Lint: ESLint + the TS plugin; this also feeds the CI `frontend` job.

## Milestones
1. **M1 (slice):** the bare page from Phase 1 — just prove trades arrive over the WebSocket. Ugly is fine.
2. **M2:** `services` + `useOrderBook`/`useTradeTape` + `OrderBook`/`TradeTape` rendering live, with rAF batching.
3. **M3:** `OrderEntry` submitting real orders end to end.
4. **M4 (Phase 3):** auth flow + protected routing.
5. **M5:** latency panel + polish + the demo gif/video for your CV.
