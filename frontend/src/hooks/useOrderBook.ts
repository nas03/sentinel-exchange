// Hook that subscribes to a MarketDataSocket and maintains current order
// book state. Components consume this hook's return value and never
// touch the socket directly — that's the inversion: components depend
// on "current book state", not on "how to get book state".
//
// Build in Phase 2, step 3.

// TODO: useOrderBook(instrument: string) -> { bids, asks, isConnected }
