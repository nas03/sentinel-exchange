// Package marketdata owns the WebSocket fan-out: one connection to the
// engine's event stream in, many client WebSocket connections out.
//
// Phase 1 goal: get a tick from the engine to a browser tab over a
// WebSocket connection. Don't add auth or rate limiting here yet —
// that's Phase 3, and bolting it on later is a deliberate exercise in
// adding a cross-cutting concern without breaking existing structure.
//
// Research before writing: the "hub" pattern (central struct holding a
// map of active connections + broadcast channel) is the standard Go
// approach here — look up "gorilla websocket chat example" for the
// canonical shape, then adapt it for market data instead of chat.
package marketdata

// TODO: Hub struct — registered clients, broadcast channel, register/unregister channels
// TODO: ServeWS — upgrades HTTP to WebSocket, registers client with hub
// TODO: connection to engine IPC — reads engine events, pushes onto broadcast channel
