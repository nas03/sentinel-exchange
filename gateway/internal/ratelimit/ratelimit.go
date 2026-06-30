// Package ratelimit implements a token bucket limiter applied per
// authenticated client (or per IP for unauthenticated endpoints).
//
// Phase 3 build. Test this explicitly: send requests faster than the
// bucket refills and confirm you get rejected with a clear error —
// write that test down in docs/02-THREAT-MODEL.md's validation section.
package ratelimit

// TODO: TokenBucket struct — capacity, tokens, refill rate, last refill time
// TODO: Allow() method
// TODO: Middleware wrapping an http.Handler
