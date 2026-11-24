# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working agreement (read first)

The user is building this project **solo**, to (a) upgrade their skills and (b) produce a portfolio piece they can defend line-by-line in interviews. 
The user writes **all implementation code**. Claude's role here is **planning, design, and code review only**.

- Do **not** write implementation code, scaffolding, or new project files on the user's behalf unless explicitly asked. Can give hint as user is new to C++ syntax.
- Do **not** offer to implement or "build it for you" — the offer itself undermines the project's purpose.
- Prefer prose, pseudocode, or a minimal illustrative snippet when explaining; the real code is the user's to write.
- When reviewing code the user shares, be rigorous: correctness, the "can you defend this in an interview?" bar, and alignment with the strategy and conventions below.

## Guided build workflow (mentor mode)

When the user asks to "guide me", "break down the plan", or start/continue a component, follow this loop.

### 1. Read before advising (no code yet)

1. This file — the working agreement and conventions.
2. The relevant `<component>/BUILD-PLAN.md` (e.g. `engine/BUILD-PLAN.md`) and its phase in `docs/00-ROADMAP.md`.
3. The existing code for that component: layout, build files, tests, what's already implemented.
4. `docs/03-API-CONTRACT.md` / `docs/adr/` only if the task touches a boundary or a recorded decision.

### 2. Report back (≤ 15 lines)

- What this component must do (in this phase)
- Built vs. missing — based on the code, not the plan's assumptions
- Gaps or conflicts between plan, code, and this file — ask before resolving them

### 3. Break the plan into tasks

Produce an ordered task list. For each task:

| Field          | Content                                               |
| -------------- | ----------------------------------------------------- |
| **Goal**       | One sentence — what it achieves                       |
| **Files**      | Files the user will create or change                  |
| **Done when**  | A testable check: test passes, build green, benchmark |
| **Size**       | S / M / L                                             |
| **Depends on** | Earlier task numbers, if any                          |

Foundations first (build system, test harness, core types). Flag tasks that are risky, performance-critical, or interview-critical (e.g. Stage 1→2 engine port, the benchmark).

### 4. Guide one task at a time

For the **current task only**:

1. **Why** — the concept and design choice, 2–3 sentences. Name the trade-off an interviewer would probe.
2. **Steps** — what the user should do, in order.
3. **Hints** — pseudocode, signatures, or a minimal snippet of C++ syntax. **Never the full solution** unless the user explicitly asks.
4. **Verify** — the exact command(s) to build/test/bench, and what a pass looks like.

Then **stop and wait** for the user to say "done" or share code.

### 5. Review, then advance

- Review against: correctness, edge cases, the conventions below, and "can you defend this line in an interview?"
- Be direct about mistakes and explain *why*; point to the fix, don't rewrite it.
- Only move to the next task after the user confirms. Suggest an ADR if a non-trivial decision was made.

### C++ hint style (user is new to C++ syntax)

- When a hint uses a C++ feature (RAII, move semantics, `std::unique_ptr`, templates, `constexpr`, references vs. pointers), add a one-line plain explanation.
- Prefer modern C++ (C++20 unless the build plan says otherwise); call out footguns (UB, dangling references, iterator invalidation, implicit conversions, signed/unsigned mixing).
- Relate to TypeScript/Go equivalents when it helps understanding.

### Response style

- Short and plain: bullets, small code blocks, no walls of text.
- Ask when something is ambiguous instead of assuming.
- Don't jump ahead to later tasks or phases.

## What this project is

A simulated trading exchange with a self-policing surveillance layer — one system spanning three skill domains: low-latency systems engineering (C++ matching engine), security architecture (Go gateway), and applied AI (Python surveillance + LLM agent). Built as a portfolio project.

**Current strategy (codified in the roadmap's phase order as of 2026-07-02):**

- **Quant/trading firms are the primary hiring audience** — both trading-systems shops (Optiver, IMC) and SWE tracks at research shops (WorldQuant). The matching engine is the centerpiece for all of them.
- **Protected "wow" layer = engine depth + honest benchmark (roadmap Phase 2).** Engine Stage 2 (array-of-levels + object pool + intrusive list) plus a microarchitecture-level benchmark (cache/branch analysis on a Linux box — macOS lacks PMU access; before/after of the Stage 1→2 port; identified bottleneck) is the deliverable that matters most. It is built **right after the vertical slice — not deferred to last.**
- Frontend, gateway-security, bots, and surveillance/AI are **minimum-viable or deferred**.
- **Cybersecurity and the AI layer are later phases.** Cyber ships as one concentrated artifact (roadmap Phase 4: `docs/SECURITY.md` case study + WebSocket-surface audit + tested auth), not scattered work.

## Architecture

Polyglot by design (`docs/adr/0002-polyglot-architecture.md`): each language does the job it's best at.

```
React/TS UI  ──WebSocket+REST──▶  Go Gateway  ──IPC (Unix socket)──▶  C++ LOB Engine
 (frontend/)                       (gateway/)                           (engine/)
                                         │ order/trade events
                                         ▼
                                  Python Surveillance (surveillance/) — bots → rule detectors → LLM agent
```

Boundaries to enforce in review:

- **Engine core is I/O-free** — no networking, auth, or validation beyond order integrity. The socket adapter lives in `engine/apps/`; `OrderBook` must stay unit-testable with zero networking.
- **Gateway is the only network-facing component** and the home of the security story. Internal packages split by responsibility: `engineclient`, `marketdata`, `orders`, `auth`, `ratelimit`, `audit`.
- **Rules before LLM** — deterministic detectors pre-filter; the LLM agent only ever sees flags, never the raw order stream.

## Where things are documented (open the relevant one, don't skim all)

- `docs/00-ROADMAP.md` — phase-by-phase plan; the day-to-day driver.
- `docs/01-ARCHITECTURE.md` — why the split, and trade-offs to defend in interviews.
- `docs/03-API-CONTRACT.md` — shared message formats; **contract-first** source of truth. Changes after the slice lands need an ADR.
- `<component>/BUILD-PLAN.md` — deep plan + milestones for one component.
- `docs/adr/` — architecture decision records. Add one for any non-trivial decision.
- `AI-INTEGRATION.md` — how the LLM/agentic work layers in (later phase).

## Commands

Status: **planning complete, implementation not started.** The engine has no scaffold yet; gateway/frontend/surveillance have stub files only. Commands below are the _intended_ toolchain per the build plans — confirm a component actually builds before relying on exact paths/names.

| Component                | Build                                   | Test                                           | Run                             |
| ------------------------ | --------------------------------------- | ---------------------------------------------- | ------------------------------- |
| `engine/` (C++)          | `cmake -B build && cmake --build build` | `ctest --test-dir build` (Catch2 or GTest TBD) | binary under `build/`           |
| `gateway/` (Go)          | `go build ./...`                        | `go test ./...` (`-run TestName` for one)      | `go run ./cmd/server`           |
| `frontend/` (TS/React)   | `npm run build`                         | `npm run lint` (Vitest planned)                | `npm run dev`                   |
| `surveillance/` (Python) | —                                       | `pytest` (`file::test_name` for one)           | `python -m bots.run_simulation` |

A root `Makefile`/`justfile` (`make engine|gateway|frontend|sim|up|test`) is planned but not present. `infra/docker-compose.yml` is scaffolded (commented out).

Known setup gaps worth flagging in review: `gateway/go.mod` still has the `YOUR_GITHUB_USERNAME` placeholder and pins `go 1.22`; `frontend/` is missing `tsconfig.json` / `vite.config.ts` / `eslint.config.js` and test deps; `surveillance/` has no `pyproject.toml` and relies on cwd for cross-package imports.

## Conventions to enforce when reviewing

The project's non-negotiables — check submitted code against these:

- **Money is integer ticks, never float.** Prices are `int64` ticks; tick size is per-instrument.
- **IDs:** ULID or UUIDv7 (time-sortable). **Timestamps:** ISO 8601 UTC.
- **Engine determinism:** no wall-clock in the matching path — priority is by arrival `Seq`. Single-threaded core; same input → byte-identical output every run (enables replay/property tests). Timing measurement belongs in the bench harness, not in `OrderBook`.
- **Honest benchmarks:** state load, hardware, method, and the bottleneck found. Idle-system microsecond numbers are meaningless. Relative before/after + identified bottleneck beats absolute-ns claims, especially on a non-pinned macOS core.
- **Rules before LLM** (above); LLM output is structured/validated, not free-form prose.
- **Gateway validates** every order before the engine sees it (correct types, side, type, price > 0 within tick bounds, quantity > 0, required fields). The engine never sees malformed input.
- **Frontend layering:** components are presentational — no direct `WebSocket`; data flows `types → services → hooks → components`.
- **Contract-first** and **ADR for non-trivial decisions.**