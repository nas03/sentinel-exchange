# Threat Model — STRIDE

Fill this in during Phase 3 (security hardening week). The structure is pre-built; the content is the actual work — don't skip to filling generic answers. For each row, write what's *specific to this system*.

## Scope

What's in scope: gateway, frontend auth flow, order submission path, WebSocket data feed.
What's out of scope (for now, document why): the matching engine's internal logic (trusted, not network-exposed directly), infra-level concerns like cloud IAM (covered separately in phase 2).

## Assets to protect

- User credentials / session tokens
- Order integrity (no unauthorized order modification)
- Market data integrity (no falsified price feed)
- Audit log integrity (tamper-evidence)
- System availability (resistant to flooding/DoS)

## STRIDE pass

For each category: what's the threat, where in the system, what's the mitigation, what's the residual risk you're accepting (be honest — every project has some).

### Spoofing (identity)
| Threat | Component | Mitigation | Residual risk |
|---|---|---|---|
| e.g. attacker forges JWT | gateway/auth | | |
| e.g. WebSocket connection hijacking | gateway/marketdata | | |

### Tampering
| Threat | Component | Mitigation | Residual risk |
|---|---|---|---|
| e.g. order payload modified in transit | gateway/orders | | |
| e.g. audit log entries altered after write | gateway audit logging | | |

### Repudiation
| Threat | Component | Mitigation | Residual risk |
|---|---|---|---|
| e.g. user denies placing an order | audit log | | |

### Information Disclosure
| Threat | Component | Mitigation | Residual risk |
|---|---|---|---|
| e.g. one user's orders visible to another | gateway/orders | | |
| e.g. verbose error messages leak internals | gateway error handling | | |

### Denial of Service
| Threat | Component | Mitigation | Residual risk |
|---|---|---|---|
| e.g. order flood from single client | gateway/ratelimit | | |
| e.g. WebSocket connection exhaustion | gateway/marketdata | | |

### Elevation of Privilege
| Threat | Component | Mitigation | Residual risk |
|---|---|---|---|
| e.g. regular user accesses admin endpoints | gateway/auth | | |

## How you'll validate mitigations

List the actual test you'll run for each major mitigation (e.g. "send 1000 orders/sec from one client, confirm rate limiter rejects after threshold X" — then actually run it and note the result here).

## What you'd do with more time

Be honest about what's out of scope for the portfolio version vs. what a production system would need (e.g. proper secrets management, mTLS between gateway and engine, formal pen test). This honesty is itself a good interview signal — it shows you know the difference between "demo secure" and "production secure."
