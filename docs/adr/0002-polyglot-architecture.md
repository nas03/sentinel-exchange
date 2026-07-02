# ADR 0002: Polyglot architecture (C++ / Go / TypeScript / Python)

## Status
Accepted

## Context
Could build this entire system in TypeScript (Node backend + React frontend), which would be faster to iterate on and play to existing strength. Need to decide whether the added complexity of four languages is worth it for a portfolio project.

## Decision
Use C++ for the matching engine, Go for the gateway, TypeScript/React for the frontend, Python for the surveillance/AI layer.

## Alternatives considered
- **All TypeScript/Node**: faster initial velocity, one language to maintain. Rejected because the matching engine is the centerpiece of the "performance engineering" story — a Node-based matching engine doesn't demonstrate the same depth, and trading firms specifically look for comfort with lower-level languages.
- **All Go**: Go could plausibly handle the matching engine too (and would simplify the engine/gateway boundary into one process). Considered, but C++ is more standard for matching cores in the actual industry and is a stronger signal for the systems-engineering story specifically.
- **Rust instead of C++ for the engine**: genuinely viable alternative, arguably a better safety story. Not chosen for v1 because it adds a learning curve on top of the systems-design learning curve already planned; worth revisiting as a much later rewrite if time allows, since "I rewrote the hot path in Rust for memory safety" is itself a good interview story.

## Consequences
**Easier:** each component can be discussed in depth on its own terms; the project naturally demonstrates breadth across the stack; each language is doing the job it's actually suited for.

**Harder:** four toolchains to keep working together, an IPC boundary to design carefully, more surface area for environment/setup friction. Mitigate with `infra/docker-compose.yml` so the whole stack runs with one command despite the language mix.

**Trade-off accepted:** slower initial velocity than a single-language stack, in exchange for a stronger and more defensible portfolio narrative.
