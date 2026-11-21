#pragma once
// types.hpp
#include <cstdint>

using Price = std::int64_t; // integer ticks, NEVER float for money
using Quantity = std::int64_t;
using OrderId = std::uint64_t;
using Seq = std::uint64_t; // logical time — replaces wall-clock

enum class Side
{
    Buy,
    Sell
};
enum class Type
{
    Limit,
    Market
};

struct Order
{
    OrderId id{};
    Side side{};
    Price price{};
    Quantity quantity{}; // remaining quantity
    Seq seq{};           // arrival order — this is your "time" priority
    Type type{};
    // Stage 2: intrusive pointers (prev/next within level), parent level ptr
};