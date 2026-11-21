#include <iostream>
#include <vector>
#include "event.hpp"

const char *side_name(Side s)
{
    return s == Side::Buy ? "buy" : "sell";
}

std::vector<Event> add(const Order &order)
{
    return {Event{.kind = Event::Kind::OrderAck, .seq = order.seq}};
}
int main()
{
    Order order{1, Side::Buy, 10200, 120, 7};
    std::cout << side_name(order.side);
    std::cout << order.id;
    std::cout << order.price;
    std::cout << order.quantity;
    std::cout << order.seq;
}
