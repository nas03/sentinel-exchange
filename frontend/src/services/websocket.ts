// WebSocket connection management — reconnect logic and message parsing
// live here, NOT in components or hooks. This is the one place that
// knows about the raw WebSocket API; everything else consumes a typed
// event interface.
//
// Build this in Phase 2, step 2 (after types/ is settled). Research
// exponential backoff reconnect strategies before writing this — a
// naive immediate-retry loop will hammer the gateway on disconnect.

import type { MarketDataMessage } from "../types/api";

export type MarketDataListener = (msg: MarketDataMessage) => void;

export class MarketDataSocket {
  // TODO: constructor(url: string)
  // TODO: connect() — opens WebSocket, parses incoming JSON into MarketDataMessage
  // TODO: onMessage(listener: MarketDataListener) — subscribe
  // TODO: reconnect logic with exponential backoff on close/error
  // TODO: close()
}
