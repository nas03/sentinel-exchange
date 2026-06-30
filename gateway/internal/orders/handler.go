// Package orders handles order submission and cancellation: validates
// the request shape, forwards valid orders to the engine over IPC, and
// returns the ack/reject to the client.
//
// Validation here is about message integrity (right types, in-bounds
// values) — NOT business logic like "does this user have sufficient
// balance" (out of scope for this project, document that choice).
package orders

// TODO: SubmitOrder handler — validate against docs/03-API-CONTRACT.md schema, forward to engine
// TODO: CancelOrder handler
// TODO: engine IPC client (likely shared with marketdata package — consider where that connection should live)
