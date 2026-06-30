# Engine — Build Plan (C++, ground-up rebuild)

Clean rebuild. The old LOB project is abandoned; we keep the *lessons*, not the code. This is the centerpiece for trading-firm interviews, so correctness and a defensible design matter more than raw feature count.

## Design goals (and non-goals)

**Goals**
- Correct price-time priority matching for a single instrument
- O(1) cancel, fast add, deterministic output
- Every book mutation emits an event (feeds market data + audit + surveillance)
- Fully testable in isolation, with a deterministic replay harness
- Honest, load-tested performance numbers with an identified bottleneck

**Non-goals (v1 — say no to these on purpose)**
- Multiple instruments (add later via sharding — know the answer, don't build it yet)
- Threading / lock-free structures (a correct single-threaded core first; concurrency is a later, measured optimization)
- Persistence / crash recovery
- Wall-clock anywhere in the matching path (use sequence numbers — see Determinism)

## The core design decision: order book representation

This is the single most important choice and the thing interviewers will probe. Build it in two stages.

### Stage 1 — correctness first (map-based)

```
price levels:  std::map<Price, Level>   (ordered; bids reverse, asks forward)
each Level:    FIFO list of orders (std::list or intrusive doubly-linked list)
order lookup:  std::unordered_map<OrderId, OrderHandle>  (for O(1) cancel)
```

Simple, obviously correct, easy to test. `std::map` gives ordered traversal for matching from the best price. Get every invariant passing here before optimizing anything.

### Stage 2 — the "fast LOB" optimization (measured, with before/after numbers)

The canonical fast design (look up "How to Build a Fast Limit Order Book"):

```
price levels:  flat array indexed by price tick  →  O(1) level access
each Level:    intrusive doubly-linked list of Orders (FIFO)
orders:        allocated from an object pool (no malloc in the hot path)
order lookup:  unordered_map<OrderId, Order*>  →  O(1) cancel
best bid/ask:  cached pointers, updated on mutation
```

Why this is the "real" design: array indexing is O(1) and cache-friendly; the intrusive list means cancel is pointer surgery with no search; the object pool removes allocator latency from the matching path. The catch is the array only works for a **bounded, known price range** — document that assumption.

**Do not start here.** Build Stage 1, get it correct and benchmarked, then port to Stage 2 and show the latency/throughput delta. That before/after *is* the interview story — "I measured the map version at X, identified allocation and cache misses as the bottleneck, switched to a pooled array-of-levels design, and got Y." That's worth far more than having started with the fast version and having nothing to compare against.

## Core types (header sketch — implement yourself)

```cpp
// types.hpp
using Price    = std::int64_t;  // integer ticks, NEVER float for money
using Quantity = std::int64_t;
using OrderId  = std::uint64_t;
using Seq      = std::uint64_t;  // logical time — replaces wall-clock

enum class Side  { Buy, Sell };
enum class Type  { Limit, Market };

struct Order {
    OrderId  id;
    Side     side;
    Price    price;
    Quantity quantity;       // remaining quantity
    Seq      seq;            // arrival order — this is your "time" priority
    // Stage 2: intrusive pointers (prev/next within level), parent level ptr
};
```

```cpp
// book.hpp  — owns matching logic ONLY. No networking, no auth, no validation
//             beyond order integrity.
class OrderBook {
public:
    // Returns the events produced by this action (acks, trades, book deltas).
    // The caller (gateway adapter) is responsible for emitting them.
    std::vector<Event> add(const Order& order);
    std::vector<Event> cancel(OrderId id);

    // Read-only views for market data / tests
    Price best_bid() const;
    Price best_ask() const;

private:
    std::vector<Event> match(Order& aggressor);  // crosses against the book
    // ... level storage (Stage 1: map; Stage 2: array+pool), id→order index
};
```

```cpp
// event.hpp — what the book emits. Matches docs/03-API-CONTRACT.md.
struct Event {
    enum class Kind { OrderAck, OrderReject, Trade, BookDelta } kind;
    // union/variant of payloads: ack{id}, trade{price,qty,maker,taker},
    //                            delta{side,price,new_qty}
    Seq seq;
};
```

## Matching algorithm (the rules)

1. Incoming **limit** order: if it crosses (buy price ≥ best ask, or sell price ≤ best bid), match against the opposite side starting from the best price, FIFO within each price level, generating partial fills until the order is filled or no longer crosses. Any remainder rests on the book.
2. Incoming **market** order: match against the best available prices until filled or the book is exhausted (then the remainder is cancelled — document this choice).
3. Partial fills: a resting order can be partially consumed; decrement its remaining quantity, leave it in place with its original `seq` (priority preserved).
4. Self-trade prevention: out of scope for v1, but know it exists and mention it as a known gap.

## Determinism (non-negotiable for a trading engine)

- No `std::chrono::now()` in the matching path. Priority is by arrival `Seq`, assigned as orders enter. Wall-clock timestamps, if needed for display, are attached *outside* the core.
- Single-threaded core. Given the same input sequence, the engine must produce byte-identical output every run. This is what makes the replay harness possible and is a genuinely strong correctness signal.

## Testing strategy

- **Invariants (property tests):** after every operation — book is never crossed (best_bid < best_ask); total resting quantity is conserved across add/cancel/match; no order has negative remaining quantity; every order in the id-index exists in exactly one level.
- **Golden scenarios:** hand-written sequences with known outcomes (a cross that partially fills two levels, a cancel that empties a level, a market order that walks the book). Assert exact event output.
- **Fuzz/replay:** generate long random sequences of valid operations, run them, assert all invariants hold throughout. Save any failing sequence as a regression test.
- **Determinism test:** run the same input twice, assert identical output.

Use Catch2 or GoogleTest. Tests are not optional here — "my matching engine has property-based invariant tests" is itself a strong interview line.

## Benchmarking (Phase 5, do it honestly)

Drive the engine at a sustained order rate from a generator, measure order-to-event latency (p50/p99) and max sustained throughput before latency degrades. Record hardware, load profile, and **the bottleneck you found**. See `engine/README.md` for the honesty rules — idle-system microsecond numbers are meaningless.

## Project structure

```
engine/
├── CMakeLists.txt
├── include/engine/   # public headers: types, order, event, book
├── src/              # implementations
├── tests/            # Catch2/GTest: invariants, golden, fuzz, determinism
├── bench/            # load generator + latency harness
└── apps/             # the runnable binary that wraps OrderBook + the IPC adapter
```

Keep `OrderBook` free of I/O — the IPC/socket adapter that talks to the gateway lives in `apps/`, takes events from the book, and writes them to the socket. That separation keeps the core unit-testable with zero networking.

## Milestones

1. **M1 — Correct core (Stage 1):** `OrderBook` with add/cancel/match over a `std::map`, full event emission, all invariant + golden + determinism tests passing. No networking yet.
2. **M2 — Runnable + wired:** the `apps/` binary reads orders from a Unix socket, runs them through the book, writes events back out. This is the engine's half of the Phase 1 vertical slice.
3. **M3 — Fast LOB (Stage 2):** port to array-of-levels + object pool + intrusive lists. Re-run all tests (they should still pass — that's the point of having them).
4. **M4 — Benchmark:** load harness, honest numbers, documented bottleneck and the fix you made.

Done with the engine when M2 is working (slice unblocked) — M3/M4 are the depth that impresses trading firms, do them after the rest of the system is demoable.
