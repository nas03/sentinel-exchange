// Package audit is the append-only, structured record of every order
// event: actor, action, order detail, timestamp, sequence. This is the
// Repudiation mitigation in docs/02-THREAT-MODEL.md.
//
// Build in Phase 3. Keep the writer behind an interface (a file is fine
// for v1). Note in the threat model that production would want
// tamper-evidence (hash chaining / WORM) — naming the gap is itself a
// good signal.
package audit

// TODO: Logger interface { Record(event AuditEvent) error }
// TODO: file-backed JSON-lines implementation
// TODO: wire into the orders + auth handlers via middleware
