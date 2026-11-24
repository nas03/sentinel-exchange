# PROGRESS

Implementation log. READ at the start of a coding session; update before ending one.
(If renamed/moved, update the CLAUDE.md "outfile" instruction to match.)

## Engine — M1: correct core (Stage 1, map-based book)

Status: **in progress** (kickoff + task breakdown done 2026-11-25).

1. [ ] Repo hygiene: `git rm --cached engine/main`; .gitignore for `engine/main`, `engine/test_book`, `build/`
2. [ ] `book.hpp` declaration-only — decisions: two maps w/ flipped comparators (best = `begin()`), `Level` = FIFO `std::list<Order>`, `unordered_map<OrderId, list::iterator>` cancel index, seq ticks once per accepted action
3. [ ] Golden test #1, red first (bid 10200×100 + 10100×50, sell 10200×120 → Trade(10200,100), level gone, 20 rests as ask 10200). **Gate: header + test reviewed with Claude before book.cpp**
4. [ ] `book.cpp`: add() + match loop until golden #1 passes (sanitizers on)
5. [ ] cancel() + golden tests (mid-level, level-emptying, unknown-id semantics per API contract DELETE)
6. [ ] Invariant checker after every op (never crossed, no ≤0 qty, index↔book consistency, qty conserved)
7. [ ] Golden round 2: multi-level partial fill, market walks book to exhaustion, price-time priority within a level
8. [ ] Determinism test (same ops twice → identical events) — must survive the Stage 2 port unchanged
9. [ ] Close M1: commit, update this file, next = M2 (`apps/` binary + Unix-socket adapter, JSON-lines per `docs/03-API-CONTRACT.md`)

## Done

- 2026-11-22 (f709561): `types.hpp` + `event.hpp` committed; C++20 settled (designated initializers in use)
- 2026-11-25: earlier book.cpp/book.hpp/test_book.cpp attempt deleted — clean slate on the OrderBook; M1 kickoff decisions made (captured in task 2)
