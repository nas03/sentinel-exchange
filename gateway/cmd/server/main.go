// Sentinel Exchange — Gateway entry point.
//
// Wires together the engine IPC connection, the WebSocket market data hub,
// order/auth/ratelimit middleware, and starts the HTTP server.
//
// Build this LAST, once the internal packages exist — main.go should be
// mostly wiring, not logic. If logic creeps in here, it probably belongs
// in one of the internal packages instead.
package main

func main() {
	// TODO Phase 1: load config, connect to engine IPC
	// TODO Phase 1: start marketdata hub, register WebSocket handler
	// TODO Phase 1: register orders REST handlers
	// TODO Phase 3: wrap handlers with auth + ratelimit middleware
	// TODO: start HTTP server
}
