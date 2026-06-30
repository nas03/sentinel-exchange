// Package engineclient owns the single connection to the C++ engine over
// its Unix domain socket. It's the only package that knows the engine's
// wire format — keep framing logic here so a later switch to a binary
// protocol touches nothing else.
//
// Build FIRST (gateway M1). Both orders and marketdata depend on this.
package engineclient

// EngineClient is the interface everything else codes against — mock it
// in tests so the gateway is testable without the engine running.
//
// type EngineClient interface {
//     SubmitOrder(ctx context.Context, o Order) error
//     Events() <-chan Event
// }
//
// TODO: dial the Unix socket (path from config)
// TODO: reconnect with backoff if the engine restarts
// TODO: read line-delimited JSON events, push onto the Events() channel
// TODO: write order submissions to the socket
