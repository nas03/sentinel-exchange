// Shared types mirroring docs/03-API-CONTRACT.md.
// Keep this file as the single source of truth for the frontend's view of
// the wire format — if the contract changes, update here first, then let
// TypeScript's type errors guide you to every place that needs updating.

export type Side = "buy" | "sell";
export type OrderType = "limit" | "market";
export type OrderStatus = "accepted" | "rejected";

export interface OrderRequest {
  instrument: string;
  side: Side;
  type: OrderType;
  price: number; // integer ticks, not float — see API contract conventions
  quantity: number;
  clientOrderId: string;
}

export interface OrderResponse {
  orderId: string;
  status: OrderStatus;
  rejectReason: string | null;
}

// Discriminated union for WebSocket market data messages — this is the
// TypeScript pattern that makes the message handler exhaustive and
// type-safe (switch on `type`, no `any` needed).
export type MarketDataMessage = BookUpdateMessage | TradeMessage;

export interface BookUpdateMessage {
  type: "book_update";
  instrument: string;
  side: Side;
  price: number;
  quantity: number;
  timestamp: string;
}

export interface TradeMessage {
  type: "trade";
  instrument: string;
  price: number;
  quantity: number;
  timestamp: string;
  tradeId: string;
}

// TODO: as auth lands in Phase 2/3, add AuthTokens, LoginRequest, etc. here
