# Infra — Build Plan

Keep this lean and incremental. Infra exists to make the other four components easy to run and easy to trust — don't build it ahead of need. Resist the urge to containerize and orchestrate everything in week one; that's effort that produces no demoable feature.

## Layer 1 — Local dev ergonomics (do this early, it pays off daily)

The polyglot stack is the cost you accepted (see ADR 0002); good local tooling is how you pay it down.

- **A root `Makefile` or `justfile`** with one-word targets so you never memorize four toolchains' incantations:
  ```
  make engine     # build + run the C++ engine binary
  make gateway    # go run the gateway
  make frontend   # npm run dev
  make sim        # python -m bots.run_simulation
  make up         # bring up the whole stack (engine + gateway) together
  make test       # run every component's tests
  ```
- **Keep the frontend out of Docker** during development — `npm run dev` with hot reload is far faster to iterate on. Containerize it last, if at all (only really needed for the deploy phase).
- The engine↔gateway pair is the part worth a `docker-compose` once the slice works, because they share the Unix socket — a shared volume makes that clean. The compose file is scaffolded (commented) in `infra/docker-compose.yml`; uncomment services as they become runnable, in this order: engine → gateway → (later) prometheus + grafana.

## Layer 2 — CI (grows with the project)

`.github/workflows/ci.yml` is scaffolded with per-component jobs. Fill them in as each component gains something to check:
- **engine:** build with CMake, run the test suite (invariants/golden/determinism).
- **gateway:** `go vet`, `go test ./...`.
- **frontend:** `tsc --noEmit`, lint, Vitest.
- **surveillance:** `pytest`.

Keep CI green from the start — a project with passing CI badges reads as more professional at a glance, and red CI on a portfolio repo is a bad look.

## Layer 3 — Security in CI (Phase 3 — this is cyber-role evidence)

This is the part that actually speaks to Orro/cyber roles, so make it real:
- **SAST:** add Semgrep across the repo (it covers Go/TS/Python). Fix findings or consciously document accepted ones.
- **Dependency scanning:** `govulncheck` (Go), `npm audit` (frontend), `pip-audit` (surveillance).
- **Prove it works:** deliberately introduce a known-vulnerable dependency or an obvious injection sink, confirm CI catches it, then revert. Note that test in `docs/02-THREAT-MODEL.md` — "my pipeline fails on known-bad input, here's the evidence" is a concrete secure-SDLC story.
- **Secrets hygiene:** secret-scanning (e.g. gitleaks) in CI; nothing sensitive ever committed (`.env` is gitignored already).

## Layer 4 — Observability (Phase 5, for the benchmark)

- The gateway exposes `/metrics` (Prometheus format): order counts, active WebSocket connections, latency histograms.
- `infra/prometheus.yml` scrapes the gateway; Grafana visualizes. Both are scaffolded (commented) in the compose file.
- **Honesty rule applies:** these dashboards are only meaningful under real load. The latency numbers come from the engine's load harness (`engine/bench/`), driven hard, with the methodology written down. A pretty panel over an idle system is theatre — see `engine/BUILD-PLAN.md`.

## Layer 5 — Deployment (Phase 6 — optional, months out)

Only after the local system is complete and demoable. This doubles as cloud/security evidence (ties into your AWS Developer Associate work).

- **AWS, least-privilege from the start:** scoped IAM roles per service, a VPC with private subnets for the engine/gateway, secrets in SSM Parameter Store or Secrets Manager (never env files in prod).
- **Write it up as the real deliverable.** A short architecture doc — network diagram, IAM boundary, secrets flow, what you'd add for production (mTLS between gateway and engine, WAF, proper logging/alerting) — is worth more to a cyber interviewer than the deployment itself running.
- A note on doing the deploy: provisioning, IAM changes, and anything touching real cloud credentials are things you should run and authorize yourself — keep those actions in your own hands rather than automating them blindly.

## Sequencing summary

| When | Build |
|---|---|
| Early (alongside Phase 1) | Root Makefile/justfile, engine+gateway docker-compose |
| As components mature | Per-component CI jobs, keep green |
| Phase 3 | SAST + dep scanning + secret scanning + the "prove it catches a vuln" test |
| Phase 5 | Prometheus/Grafana, fed by honest load-tested numbers |
| Phase 6 (months out) | AWS deploy + the security writeup |

Don't run ahead of this table. Infra that isn't unblocking a feature or a security story is premature.
