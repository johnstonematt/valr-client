from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass
from typing import List, Optional, TypeAlias, TypedDict

from valrpy.enums import OrderSide, TransactionType, OrderType, WebsocketMessageType
from valrpy.utils import parse_to_datetime, parse_to_bool


__all__ = [
    "AggregatedOrderbookData",
    "FullOrderbookData",
    "MarketSummaryData",
    "TradeBucketData",
    "NewTradeData",
    "OpenOrderInfo",
    "OpenOrdersUpdateData",
    "BalanceUpdateData",
    "NewAccountHistoryRecordData",
    "NewAccountTradeData",
    "InstantOrderCompletedData",
    "OrderProcessedData",
    "OrderStatusUpdateData",
    "FailedCancelOrderData",
    "NewPendingReceiveData",
    "SendStatusUpdateData",
    "MessageData",
    "ParsedMessage",
    "RawMessage",
]


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

    @classmethod
    def from_raw(cls, raw: dict) -> "AggregatedOrderbookLevel":
        return cls(
            side=OrderSide(raw["side"].upper()),
            quantity=Decimal(raw["quantity"]),
            price=Decimal(raw["price"]),
            currency_pair=raw["currencyPair"],
            order_count=raw["orderCount"],
        )


@dataclass
class AggregatedOrderbookData:
    """
    Aggregated orderbook.
    """

    asks: List[AggregatedOrderbookLevel]
    bids: List[AggregatedOrderbookLevel]
    last_change: datetime
    sequence_number: int

    @classmethod
    def from_raw(cls, raw: dict) -> "AggregatedOrderbookData":
        return cls(
            asks=[
                AggregatedOrderbookLevel.from_raw(raw=level) for level in raw["Asks"]
            ],
            bids=[
                AggregatedOrderbookLevel.from_raw(raw=level) for level in raw["Bids"]
            ],
            last_change=parse_to_datetime(date_str=raw["LastChange"]),
            sequence_number=int(raw["SequenceNumber"]),
        )


@dataclass
class OrderbookOrder:
    """
    Order-summary in an orderbook.
    """

    order_id: str
    quantity: Decimal

    @classmethod
    def from_raw(cls, raw: dict) -> "OrderbookOrder":
        return OrderbookOrder(
            order_id=raw["orderId"],
            quantity=Decimal(raw["quantity"]),
        )


@dataclass
class OrderbookLevel:
    """
    Orderbook-level in an orderbook.
    """

    price: Decimal
    orders: List[OrderbookOrder]

    @classmethod
    def from_raw(cls, raw: dict) -> "OrderbookLevel":
        return OrderbookLevel(
            price=Decimal(raw["price"]),
            orders=[OrderbookOrder.from_raw(raw=order) for order in raw["orders"]],
        )


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

    @classmethod
    def from_raw(cls, raw: dict) -> "FullOrderbookData":
        return cls(
            last_change=int(raw["lastChange"]),
            asks=[OrderbookLevel.from_raw(raw=level) for level in raw["Asks"]],
            bids=[OrderbookLevel.from_raw(raw=level) for level in raw["Bids"]],
            sequence_number=int(raw["sequenceNumber"]),
            checksum=int(raw["checksum"]),
        )


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

    @classmethod
    def from_raw(cls, raw: dict) -> "MarketSummaryData":
        return cls(
            currency_pair=raw["currencyPair"],
            ask_price=Decimal(raw["askPrice"]),
            bid_price=Decimal(raw["bidPrice"]),
            last_traded_price=Decimal(raw["lastTradedPrice"]),
            previous_close_price=Decimal(raw["previousClosePrice"]),
            base_volume=Decimal(raw["baseVolume"]),
            high_price=Decimal(raw["highPrice"]),
            low_price=Decimal(raw["lowPrice"]),
            created_at=parse_to_datetime(date_str=raw["createdAt"]),
            change_from_previous=Decimal(raw["changeFromPrevious"]),
            mark_price=Decimal(raw["markPrice"]),
        )


@dataclass
class TradeBucketData:
    """
    data-format for trade bucket
    """

    currency_pair_symbol: str
    bucket_period_in_seconds: int
    start_time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    @classmethod
    def from_raw(cls, raw: dict) -> "TradeBucketData":
        return cls(
            currency_pair_symbol=raw["currencyPairSymbol"],
            bucket_period_in_seconds=int(raw["bucketPeriodInSeconds"]),
            start_time=parse_to_datetime(date_str=raw["startTime"]),
            open=Decimal(raw["open"]),
            high=Decimal(raw["high"]),
            low=Decimal(raw["low"]),
            close=Decimal(raw["close"]),
            volume=Decimal(raw["volume"]),
        )


@dataclass
class CurrencyInfo:
    """
    data-format for currency info
    """

    symbol: str
    decimal_places: int
    is_active: bool
    short_name: str
    long_name: str
    supported_withdraw_decimal_places: int
    collateral: Optional[bool]
    collateral_weight: Optional[Decimal]
    id: Optional[int]

    @classmethod
    def from_raw(cls, raw: dict) -> "CurrencyInfo":
        return cls(
            symbol=raw["symbol"],
            decimal_places=int(raw["decimalPlaces"]),
            is_active=parse_to_bool(raw_bool=raw["isActive"]),
            short_name=raw["shortName"],
            long_name=raw["longName"],
            supported_withdraw_decimal_places=int(
                raw["supportedWithdrawDecimalPlaces"]
            ),
            collateral=parse_to_bool(raw_bool=raw.get("collateral")),
            collateral_weight=parse_to_bool(raw_bool=raw.get("collateralWeight")),
            id=int(raw["id"]) if "id" in raw else None,
        )


@dataclass
class CurrencyPairInfo:
    """
    data-format for currency-pair info
    """

    id: int
    symbol: str
    base_currency: CurrencyInfo
    quote_currency: CurrencyInfo
    short_name: str
    exchange: str
    active: bool
    min_base_amount: Decimal
    max_base_amount: Decimal
    min_quote_amount: Decimal
    max_quote_amount: Decimal

    @classmethod
    def from_raw(cls, raw: dict) -> "CurrencyPairInfo":
        return cls(
            id=int(raw["id"]),
            symbol=raw["symbol"],
            base_currency=CurrencyInfo.from_raw(raw=raw["baseCurrency"]),
            quote_currency=CurrencyInfo.from_raw(raw=raw["quoteCurrency"]),
            short_name=raw["shortName"],
            exchange=raw["exchange"],
            active=parse_to_bool(raw_bool=raw["active"]),
            min_base_amount=Decimal(raw["minBaseAmount"]),
            min_quote_amount=Decimal(raw["minQuoteAmount"]),
            max_base_amount=Decimal(raw["maxBaseAmount"]),
            max_quote_amount=Decimal(raw["maxQuoteAmount"]),
        )


@dataclass
class NewTradeData:
    """
    data-format for new trade.
    """

    price: Decimal
    quantity: Decimal
    currency_pair: CurrencyPairInfo
    traded_at: datetime
    taker_side: OrderSide

    @classmethod
    def from_raw(cls, raw: dict) -> "NewTradeData":
        return cls(
            price=Decimal(raw["price"]),
            quantity=Decimal(raw["quantity"]),
            currency_pair=CurrencyPairInfo.from_raw(raw=raw["currencyPair"]),
            traded_at=parse_to_datetime(date_str=raw["tradedAt"]),
            taker_side=OrderSide(raw["takerSide"].upper()),
        )


@dataclass
class OpenOrderInfo:
    """
    data-format for open order update
    """

    order_id: str
    side: OrderSide
    remaining_quantity: Decimal
    original_price: Decimal
    currency_pair: CurrencyPairInfo
    created_at: datetime
    original_quantity: Decimal
    filled_percentage: Decimal
    customer_order_id: str

    @classmethod
    def from_raw(cls, raw: dict) -> "OpenOrderInfo":
        return cls(
            order_id=raw["orderId"],
            side=OrderSide(raw["orderSide"].upper()),
            remaining_quantity=Decimal(raw["remainingQuantity"]),
            original_price=Decimal(raw["originalPrice"]),
            currency_pair=CurrencyPairInfo.from_raw(raw=raw["currencyPair"]),
            created_at=parse_to_datetime(date_str=raw["createdAt"]),
            original_quantity=Decimal(raw["originalQuantity"]),
            filled_percentage=Decimal(raw["filledPercentage"]),
            customer_order_id=raw["customerOrderId"],
        )


OpenOrdersUpdateData: TypeAlias = List[OpenOrderInfo]


@dataclass
class BalanceUpdateData:
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

    @classmethod
    def from_data(cls, raw: dict) -> "BalanceUpdateData":
        return cls(
            currency=CurrencyInfo.from_raw(raw=raw["currency"]),
            available=Decimal(raw["available"]),
            reserved=Decimal(raw["reserved"]),
            total=Decimal(raw["total"]),
            updated_at=parse_to_datetime(date_str=raw["updatedAt"]),
            lend_reserved=Decimal(raw["lendReserved"]),
            borrow_collateral_reserved=Decimal(raw["borrowCollateralReserved"]),
            borrowed_amount=Decimal(raw["borrowedAmount"]),
        )


@dataclass
class TransactionTypeInfo:
    """
    data-format for transaction-type info.
    """

    type: TransactionType
    description: str

    @classmethod
    def from_raw(cls, raw: dict) -> "TransactionTypeInfo":
        return cls(
            type=TransactionType(raw["type"].upper()),
            description=raw["description"],
        )


@dataclass
class HistoryRecordAdditionalInfo:
    """
    Additional info.
    """

    cost_per_coin: Decimal
    cost_per_coin_symbol: str
    currency_pair_symbol: str
    order_id: str

    @classmethod
    def from_raw(cls, raw: dict) -> "HistoryRecordAdditionalInfo":
        return cls(
            cost_per_coin=Decimal(raw["costPerCoin"]),
            cost_per_coin_symbol=raw["costPerCoinSymbol"],
            currency_pair_symbol=raw["currencyPairSymbol"],
            order_id=raw["orderId"],
        )


@dataclass
class NewAccountHistoryRecordData:
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

    @classmethod
    def from_raw(cls, raw: dict) -> "NewAccountHistoryRecordData":
        return cls(
            transaction_type=TransactionTypeInfo.from_raw(raw=raw["transactionType"]),
            debit_currency=CurrencyInfo.from_raw(raw=raw["debitCurrency"]),
            debit_value=Decimal(raw["debitValue"]),
            credit_currency=CurrencyInfo.from_raw(raw=raw["creditCurrency"]),
            credit_value=Decimal(raw["creditValue"]),
            fee_currency=CurrencyInfo.from_raw(raw=raw["feeCurrency"]),
            fee_value=Decimal(raw["feeValue"]),
            event_at=parse_to_datetime(date_str=raw["eventAt"]),
            additional_info=HistoryRecordAdditionalInfo.from_raw(
                raw=raw["additionalInfo"]
            ),
            id=raw["id"],
        )


@dataclass
class NewAccountTradeData:
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

    @classmethod
    def from_raw(cls, raw: dict) -> "NewAccountTradeData":
        return cls(
            price=Decimal(raw["price"]),
            quantity=Decimal(raw["quantity"]),
            currency_pair=raw["currencyPair"],
            traded_at=parse_to_datetime(date_str=raw["tradedAt"]),
            side=OrderSide(raw["side"].upper()),
            order_id=raw["orderId"],
            id=raw["id"],
        )


@dataclass
class InstantOrderCompletedData:
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

    @classmethod
    def from_raw(cls, raw: dict) -> "InstantOrderCompletedData":
        return cls(
            order_id=raw["orderId"],
            success=parse_to_bool(raw_bool=raw["success"]),
            paid_amount=Decimal(raw["paidAmount"]),
            paid_currency=Decimal(raw["paidCurrency"]),
            received_amount=Decimal(raw["receivedAmount"]),
            received_currency=raw["receivedCurrency"],
            fee_amount=Decimal(raw["feeAmount"]),
            fee_currency=raw["feeCurrency"],
            order_executed_at=parse_to_datetime(date_str=raw["orderExecutedAt"]),
        )


@dataclass
class OrderProcessedData:
    """
    data-format for order-processed info.
    """

    order_id: str
    success: bool
    failure_reason: str

    @classmethod
    def from_raw(cls, raw: dict) -> "OrderProcessedData":
        return cls(
            order_id=raw["orderId"],
            success=parse_to_bool(raw_bool=raw["success"]),
            failure_reason=raw["failureReason"],
        )


@dataclass
class OrderStatusUpdateData:
    """
    data-format for an order-status update.
    """

    order_id: str
    order_status_type: str
    currency_pair: CurrencyPairInfo
    original_price: Decimal
    remaining_quantity: Decimal
    original_quantity: Decimal
    order_side: OrderSide
    order_type: OrderType
    failed_reason: str
    order_updated_at: datetime
    order_created_at: datetime
    customer_order_id: str

    @classmethod
    def from_raw(cls, raw: dict) -> "OrderStatusUpdateData":
        return cls(
            order_id=raw["orderId"],
            order_status_type=raw["orderStatusType"],
            currency_pair=CurrencyPairInfo.from_raw(raw=raw["currencyPair"]),
            original_price=Decimal(raw["originalPrice"]),
            remaining_quantity=Decimal(raw["remainingQuantity"]),
            original_quantity=Decimal(raw["originalQuantity"]),
            order_side=OrderSide(raw["orderSide"].upper()),
            order_type=OrderType(raw["orderType"].upper()),
            failed_reason=raw["failedReason"],
            order_updated_at=parse_to_datetime(date_str=raw["orderUpdatedAt"]),
            order_created_at=parse_to_datetime(date_str=raw["orderCreatedAt"]),
            customer_order_id=raw["customerOrderId"],
        )


@dataclass
class FailedCancelOrderData:
    """
    data-format for a failed cancel order.
    """

    order_id: str
    message: str

    @classmethod
    def from_raw(cls, raw: dict) -> "FailedCancelOrderData":
        return cls(
            order_id=raw["orderId"],
            message=raw["message"],
        )


@dataclass
class NewPendingReceiveData:
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

    @classmethod
    def from_raw(cls, raw: dict) -> "NewPendingReceiveData":
        return cls(
            currency=CurrencyInfo.from_raw(raw=raw["currency"]),
            receive_address=raw["receiveAddress"],
            transaction_hash=raw["transactionHash"],
            amount=Decimal(raw["amount"]),
            created_at=parse_to_datetime(date_str=raw["createdAt"]),
            confirmations=int(raw["confirmations"]),
            confirmed=parse_to_bool(raw_bool=raw["confirmed"]),
        )


@dataclass
class SendStatusUpdateData:
    """
    data-format for info regarding a crypto withdrawal status update
    """

    unique_id: str
    status: str
    confirmations: int

    @classmethod
    def from_raw(cls, raw: dict) -> "SendStatusUpdateData":
        return cls(
            unique_id=raw["uniqueId"],
            status=raw["status"],
            confirmations=int(raw["confirmations"]),
        )


MessageData: TypeAlias = (
    AggregatedOrderbookData
    | FullOrderbookData
    | MarketSummaryData
    | MarketSummaryData
    | TradeBucketData
    | NewTradeData
    | OpenOrdersUpdateData
    | BalanceUpdateData
    | NewAccountHistoryRecordData
    | NewAccountTradeData
    | InstantOrderCompletedData
    | OrderProcessedData
    | OrderStatusUpdateData
    | FailedCancelOrderData
    | NewPendingReceiveData
    | SendStatusUpdateData
)


@dataclass
class ParsedMessage:
    """
    A parsed websocket message.
    """

    type: WebsocketMessageType
    data: MessageData


class RawMessage(TypedDict):
    """
    Raw message from websocket.
    """

    type: WebsocketMessageType
    data: Optional[dict | list]
