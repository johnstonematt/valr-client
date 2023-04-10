from decimal import Decimal
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional, TypeAlias

from valrpy.enums import (
    OrderSide,
    OrderType,
    TimeInForce,
    TransactionType,
    WebsocketMessageType,
)
from valrpy.messages.core import (
    MessageElement,
    CurrencyInfo,
    CurrencyPairInfo,
    AggregatedOrderbook,
    TradeBucket,
    MarketSummary,
)


__all__ = [
    "WebsocketFullOrderbook",
    "BalanceUpdate",
    "WebsocketOpenOrderInfo",
    "NewAccountTrade",
    "InstantOrderCompletedNotification",
    "OrderProcessedNotification",
    "FailedCancelOrderNotification",
    "StatusUpdate",
    "NewTrade",
    "NewAccountHistoryRecord",
    "OrderStatusUpdate",
    "NewPendingReceive",
    "MessageData",
    "ParsedMessage",
]


@dataclass
class WebsocketOrderbookOrder(MessageElement):
    """
    Websocket orderbook order.
    """

    order_id: str
    quantity: Decimal


@dataclass
class WebsocketFullOrderbookLevel(MessageElement):
    """
    Orderbook-level in an orderbook.
    """

    price: Decimal
    orders: List[WebsocketOrderbookOrder]


@dataclass
class WebsocketFullOrderbook(MessageElement):
    """
    Data-format for full orderbook update
    """

    last_change: datetime
    asks: List[WebsocketFullOrderbookLevel]
    bids: List[WebsocketFullOrderbookLevel]
    sequence_number: int
    checksum: Optional[int]


@dataclass
class BalanceUpdate(MessageElement):
    """
    data-format for balance update
    """

    currency: CurrencyInfo
    available: Decimal
    reserved: Decimal
    total: Decimal
    updated_at: datetime
    lend_reserved: Decimal
    borrow_collateral_reserved: Decimal
    borrowed_amount: Decimal


@dataclass
class WebsocketOpenOrderInfo(MessageElement):
    """
    data-format for open order update
    """

    order_id: str
    side: OrderSide
    currency_pair: str
    created_at: datetime
    original_quantity: Decimal
    filled_percentage: Decimal
    customer_order_id: Optional[str]
    quantity: Decimal
    price: Decimal
    type: OrderType
    status: str
    updated_at: datetime
    time_in_force: TimeInForce


@dataclass
class NewAccountTrade(MessageElement):
    """
    data-format for a new account trade.
    """

    price: Decimal
    quantity: Decimal
    currency_pair: str
    traded_at: datetime
    side: OrderSide
    order_id: str
    id: str


@dataclass
class InstantOrderCompletedNotification(MessageElement):
    """
    data-format for instant order completed info.
    """

    order_id: str
    success: bool
    paid_amount: Decimal
    paid_currency: Decimal
    received_amount: Decimal
    received_currency: str
    fee_amount: Decimal
    fee_currency: str
    order_executed_at: datetime


@dataclass
class OrderProcessedNotification(MessageElement):
    """
    data-format for order-processed info.
    """

    order_id: str
    success: bool
    failure_reason: str


@dataclass
class FailedCancelOrderNotification(MessageElement):
    """
    data-format for a failed cancel order.
    """

    order_id: str
    message: str


@dataclass
class StatusUpdate(MessageElement):
    """
    data-format for info regarding a crypto withdrawal status update
    """

    unique_id: str
    status: str
    confirmations: int


@dataclass
class NewTrade(MessageElement):
    """
    data-format for new trade.
    """

    price: Decimal
    quantity: Decimal
    currency_pair: CurrencyPairInfo
    traded_at: datetime
    taker_side: OrderSide


@dataclass
class HistoryRecordAdditionalInfo(MessageElement):
    """
    Additional info.
    """

    cost_per_coin: Decimal
    cost_per_coin_symbol: str
    currency_pair_symbol: str
    order_id: str


@dataclass
class TransactionTypeInfo(MessageElement):
    """
    data-format for transaction-type info.
    """

    type: TransactionType
    description: str


@dataclass
class NewAccountHistoryRecord(MessageElement):
    """
    data-format for a new account history record.
    """

    transaction_type: TransactionTypeInfo
    debit_currency: CurrencyInfo
    debit_value: Decimal
    credit_currency: CurrencyInfo
    credit_value: Decimal
    fee_currency: CurrencyInfo
    fee_value: Decimal
    event_at: datetime
    additional_info: HistoryRecordAdditionalInfo
    id: str


@dataclass
class OrderStatusUpdate(MessageElement):
    """
    data-format for an order-status update.
    """

    order_id: str
    order_status_type: str
    currency_pair: str | CurrencyPairInfo
    original_price: Decimal
    remaining_quantity: Decimal
    original_quantity: Decimal
    order_side: OrderSide
    order_type: OrderType
    failed_reason: str
    order_updated_at: datetime
    order_created_at: datetime
    customer_order_id: Optional[str]
    executed_price: Decimal
    executed_quantity: Decimal
    executed_fee: Decimal


@dataclass
class NewPendingReceive(MessageElement):
    """
    data-format for info regarding a new pending deposit.
    """

    currency: CurrencyInfo
    receive_address: str
    transaction_hash: str
    amount: Decimal
    created_at: datetime
    confirmations: int
    confirmed: bool


MessageData: TypeAlias = (
    AggregatedOrderbook
    | MarketSummary
    | TradeBucket
    | WebsocketFullOrderbook
    | BalanceUpdate
    | List[WebsocketOpenOrderInfo]
    | NewTrade
    | InstantOrderCompletedNotification
    | OrderProcessedNotification
    | FailedCancelOrderNotification
    | StatusUpdate
    | NewTrade
    | NewAccountHistoryRecord
    | OrderStatusUpdate
    | NewPendingReceive
    | NewAccountTrade
)


@dataclass
class ParsedMessage:
    """
    A parsed websocket message.
    """

    type: WebsocketMessageType
    data: MessageData
