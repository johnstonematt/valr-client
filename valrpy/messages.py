from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass
from typing import List

from valrpy.enums import OrderSide


@dataclass
class AggregatedOrderbookLevel:
    """
    Single level of an aggregated orderbook.
    """

    side: OrderSide
    quantity: Decimal
    price: Decimal
    currency_pair: str
    order_count: int


@dataclass
class AggregatedOrderbookData:
    """
    Aggregated orderbook.
    """

    asks: List[AggregatedOrderbookLevel]
    bids: List[AggregatedOrderbookLevel]
    last_change: datetime
    sequence_number: int


@dataclass
class OrderbookOrder:
    """
    Order-summary in an orderbook.
    """

    order_id: str
    quantity: Decimal


@dataclass
class OrderbookLevel:
    """
    Orderbook-level in an orderbook.
    """

    price: Decimal
    orders: List[OrderbookOrder]


@dataclass
class FullOrderbookData:
    """
    Data-format for full orderbook (snapshot + update).
    """

    last_change: int
    asks: List[OrderbookLevel]
    bids: List[OrderbookLevel]
    sequence_number: int
    checksum: int


@dataclass
class MarketSummaryData:
    """
    Data-format for market summary.
    """

    currency_pair: str
    ask_price: Decimal
    bid_price: Decimal
    last_traded_price: Decimal
    previous_close_price: Decimal
    base_volume: Decimal
    high_price: Decimal
    low_price: Decimal
    created_at: datetime
    change_from_previous: Decimal
    mark_price: Decimal
