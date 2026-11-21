#pragma once
#include "types.hpp"
#include <cstdint>

// event.hpp — what the book emits. Matches docs/03-API-CONTRACT.md.

struct Event
{
    enum class Kind
    {
        OrderAck,
        OrderReject,
        Trade,
        BookDelta
    } kind{};

    Seq seq{};
    OrderId order_id{};
    Price price{};
    Quantity quantity{};
    OrderId maker_id{};
    OrderId taker_id{};
    Side side{};
};
