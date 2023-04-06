import logging
from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass
from typing import (
    List,
    Optional,
    TypeAlias,
    TypedDict,
    Any,
    TypeVar,
    get_type_hints,
    Type,
    Dict,
)

from valrpy.constants import TIMEZONE, DATETIME_FORMAT
from valrpy.enums import OrderSide, TransactionType, OrderType, WebsocketMessageType


__all__ = [
    "AggregatedOrderbookData",
    "FullOrderbookData",
    "CurrencyInfo",
    "CurrencyPairInfo",
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
    "PairOrderTypes",
    "HistoricalMarketTrade",
    "ServerTime",
    "ApiKeyInfo",
    "SubaccountInfo",
    "BalanceSummary",
    "SubaccountBalance",
    "WalletBalance",
    "HistoricalAccountTrade",
    "WhitelistedAddress",
    "CurrencyWithdrawalInfo",
    "WithdrawalStatus",
    "HistoricalDeposit",
    "HistoricalWithdrawal",
    "BankAccountDetail",
    "BankAccountInfo",
    "BankInfo",
]

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _parse_to_desired_type(
    obj: Any,
    desired_type: Type[T],
) -> T:
    type_name = str(desired_type)
    # check that the param is present:
    if obj is None and not type_name.startswith("typing.Optional"):
        raise TypeError(f"Expected type {type_name}, but received None.")

    # handle 'Any' case:
    if type_name == Any:
        return obj

    if "[" in type_name:
        # this occurs with nested typing, i.e., str(List[Any]) == typing.List[typing.Any]
        outer_type_name = type_name.split("[")[0]
        # find the name of the class: 'typing.List' -> 'List'
        outer_type_name = outer_type_name.split(".")[-1]
        inner_types = desired_type.__args__
        if "Optional" in outer_type_name:
            if obj is None:
                return None
            else:
                result = _parse_to_desired_type(
                    obj=obj,
                    desired_type=inner_types[0],
                )
                return result

        if "list" in outer_type_name.lower():
            result = [
                _parse_to_desired_type(
                    obj=item,
                    desired_type=inner_types[0],
                )
                for item in obj
            ]
            return result

        raise TypeError(f"Unimplemented desired type: {type_name}")

    # now that we have handled generics, we can do the straight check:
    if isinstance(obj, desired_type):
        return obj

    # this is to avoid float inaccuracy such as
    # Decimal(0.0001) = 0.000100000000000000004792173602385929598312941379845142364501953125
    if issubclass(desired_type, Decimal):
        return Decimal(str(obj))

    if issubclass(desired_type, bool):
        if isinstance(obj, str):
            return obj.lower() == "true"

        else:
            raise TypeError(
                f"Can't convert object of type {type(obj).__name__} to bool."
            )

    if issubclass(desired_type, datetime):
        if isinstance(obj, (int, float)):
            return datetime.fromtimestamp(obj, tz=TIMEZONE)

        elif isinstance(obj, str):
            # there is a possibility that a timestamp is still given, but just in string format:
            if obj.isdecimal():
                return datetime.fromtimestamp(float(obj), tz=TIMEZONE)

            # VALR includes a 'Z' at the end of their datetime strings:
            obj = obj.rstrip("Z")

            # this is a strange case where sometimes a datetime will come through like '2023-04-05T14:32:5100',
            # and presumably the last 4 characters mean 51 seconds
            if len(obj) == 21:
                return datetime.strptime(obj[:-2], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=TIMEZONE)

            # VALR typically uses millisecond granularity and then appends a 'Z' at the end,
            # so we remove Z + add '000' to convert to microseconds
            return datetime.strptime(obj + "000", DATETIME_FORMAT).replace(tzinfo=TIMEZONE)

        else:
            raise TypeError(
                f"Can't convert object of type {type(obj).__name__} to datetime."
            )

    if issubclass(desired_type, MessageElement):
        if isinstance(obj, dict):
            return desired_type.from_raw(raw=obj)

        else:
            raise TypeError(
                f"Can't convert object of type {type(obj).__name__} to {desired_type.__name__}."
            )

    # this shouldn't run:
    raise TypeError(
        f"Unimplemented case of converting {type(obj).__name__} to {desired_type.__name__}."
    )


def _convert_to_snake_case(camel_case: str) -> str:
    if camel_case.islower():
        return camel_case

    snake_case = ""
    for character in camel_case:
        if character.isalpha() and character.isupper():
            snake_case += f"_{character.lower()}"

        else:
            snake_case += character

    return snake_case.lstrip("_")


def _apply_snake_case(camel_dict: Dict[str, Any]) -> Dict[str, Any]:
    snake_case_dict = {}
    for key, val in camel_dict.items():
        snake_key = _convert_to_snake_case(camel_case=key)
        snake_val = _apply_snake_case(camel_dict=val) if isinstance(val, dict) else val
        snake_case_dict[snake_key] = snake_val

    return snake_case_dict


class MessageElement:
    @classmethod
    def from_raw(cls: Type["U"], raw: dict) -> "U":
        type_hints = get_type_hints(cls.__init__)
        if "return" in type_hints:
            type_hints.pop("return")

        raw = _apply_snake_case(camel_dict=raw)

        parsed_kwargs = {}
        for param_name, desired_type in type_hints.items():
            parsed_kwargs[param_name] = _parse_to_desired_type(
                obj=raw.get(param_name),
                desired_type=desired_type,
            )

        return cls(**parsed_kwargs)


U = TypeVar("U", bound=MessageElement)


@dataclass
class AggregatedOrderbookLevel(MessageElement):
    """
    Single level of an aggregated orderbook.
    """

    side: OrderSide
    quantity: Decimal
    price: Decimal
    currency_pair: str
    order_count: int


@dataclass
class AggregatedOrderbookData(MessageElement):
    """
    Aggregated orderbook.
    """

    asks: List[AggregatedOrderbookLevel]
    bids: List[AggregatedOrderbookLevel]
    last_change: datetime
    sequence_number: int


@dataclass
class OrderbookOrder(MessageElement):
    """
    Order-summary in an orderbook.
    """

    order_id: str
    quantity: Decimal


@dataclass
class OrderbookLevel(MessageElement):
    """
    Orderbook-level in an orderbook.
    """

    price: Decimal
    orders: List[OrderbookOrder]


@dataclass
class FullOrderbookData(MessageElement):
    """
    Data-format for full orderbook (snapshot + update).
    """

    last_change: int
    asks: List[OrderbookLevel]
    bids: List[OrderbookLevel]
    sequence_number: int
    checksum: int


@dataclass
class MarketSummaryData(MessageElement):
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


@dataclass
class TradeBucketData(MessageElement):
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


@dataclass
class CurrencyInfo(MessageElement):
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


@dataclass
class CurrencyPairInfo(MessageElement):
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


@dataclass
class NewTradeData(MessageElement):
    """
    data-format for new trade.
    """

    price: Decimal
    quantity: Decimal
    currency_pair: CurrencyPairInfo
    traded_at: datetime
    taker_side: OrderSide


@dataclass
class OpenOrderInfo(MessageElement):
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


OpenOrdersUpdateData: TypeAlias = List[OpenOrderInfo]


@dataclass
class BalanceUpdateData(MessageElement):
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
class TransactionTypeInfo(MessageElement):
    """
    data-format for transaction-type info.
    """

    type: TransactionType
    description: str


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
class NewAccountHistoryRecordData(MessageElement):
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
class NewAccountTradeData(MessageElement):
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
class InstantOrderCompletedData(MessageElement):
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
class OrderProcessedData(MessageElement):
    """
    data-format for order-processed info.
    """

    order_id: str
    success: bool
    failure_reason: str


@dataclass
class OrderStatusUpdateData(MessageElement):
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


@dataclass
class FailedCancelOrderData(MessageElement):
    """
    data-format for a failed cancel order.
    """

    order_id: str
    message: str


@dataclass
class NewPendingReceiveData(MessageElement):
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


@dataclass
class SendStatusUpdateData(MessageElement):
    """
    data-format for info regarding a crypto withdrawal status update
    """

    unique_id: str
    status: str
    confirmations: int


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
class ParsedMessage(MessageElement):
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


@dataclass
class PairOrderTypes(MessageElement):
    """
    order-types available on a pair.
    """

    currency_pair: str
    order_types: List[OrderType]


@dataclass
class HistoricalMarketTrade(MessageElement):
    """
    Response format for historical trades.
    """

    price: Decimal
    quantity: Decimal
    currency_pair: str
    traded_at: datetime
    taker_side: OrderSide
    sequence_id: int
    id: str
    quote_volume: Decimal


@dataclass
class ServerTime(MessageElement):
    """
    Server-time info.
    """

    epoch_time: int
    time: datetime


@dataclass
class WithdrawalAddress(MessageElement):
    """
    Withdrawal address.
    """

    currency: str
    address: str


@dataclass
class ApiKeyInfo(MessageElement):
    """
    Api key info.
    """

    label: str
    permissions: List[str]
    added_at: datetime
    allowed_ip_address_cidr: str
    allowed_withdraw_address_list: List[WithdrawalAddress]


@dataclass
class SubaccountInfo(MessageElement):
    """
    Subaccount info.
    """

    label: str
    id: int


@dataclass
class BalanceSummary(MessageElement):
    """
    balance summary.
    """

    currency: str
    available: Decimal
    reserved: Decimal
    total: Decimal
    updated_at: datetime


@dataclass
class SubaccountBalance(MessageElement):
    """
    Subaccount balance.
    """

    account: SubaccountInfo
    balances: List[BalanceSummary]


@dataclass
class WalletBalance(MessageElement):
    """
    Wallet balance.
    """

    currency: str
    available: Decimal
    reserved: Decimal
    total: Decimal
    updated_at: datetime
    lend_reserved: Decimal
    borrow_reserved: Decimal
    borrowed_amount: Decimal


@dataclass
class HistoricalAccountTrade(MessageElement):
    """
    Response format for historical account trades.
    """

    price: Decimal
    quantity: Decimal
    currency_pair: str
    traded_at: datetime
    side: OrderSide
    sequence_id: int
    id: str
    order_id: str


@dataclass
class WhitelistedAddress(MessageElement):
    """
    whitelisted address
    """

    id: str
    label: str
    currency: str
    address: str
    created_at: datetime


@dataclass
class CurrencyWithdrawalInfo(MessageElement):
    """
    Withdrawal info
    """

    currency: str
    minimum_withdraw_amount: Decimal
    withdrawal_decimal_places: int
    is_active: bool
    withdraw_cost: Decimal
    supports_payment_reference: bool


@dataclass
class WithdrawalStatus(MessageElement):
    """
    Withdrawal status
    """

    currency: str
    address: str
    amount: Decimal
    fee_amount: Decimal
    transaction_hash: str
    confirmations: int
    last_confirmation_at: datetime
    unique_id: str
    created_at: datetime
    verified: bool
    status: str


@dataclass
class HistoricalDeposit(MessageElement):
    """
    Historical deposit.
    """

    currency_code: str
    receive_address: str
    transaction_hash: str
    amount: Decimal
    created_at: datetime
    confirmations: int
    confirmed: bool
    confirmed_at: Optional[datetime]


@dataclass
class HistoricalWithdrawal(MessageElement):
    """
    Withdrawal.
    """

    currency: str
    address: str
    amount: Decimal
    fee_amount: Decimal
    confirmations: int
    last_confirmation_at: Optional[datetime]
    unique_id: str
    created_at: datetime
    verified: bool
    status: str


@dataclass
class BankAccountInfo(MessageElement):
    """
    Bank account info.
    """

    id: str
    bank_code: str
    bank_name: str
    account_holder: str
    account_number: str
    branch_code: str
    account_type: str
    status: str
    inserted_at: datetime
    updated_at: datetime
    country: str
    currency: Optional[CurrencyInfo]


@dataclass
class BankAccountDetail(MessageElement):
    """
    Details regarding a bank account
    """

    id: str
    bank: str
    account_holder: str
    account_number: str
    branch_code: str
    account_type: str
    created_at: datetime
    country: str


@dataclass
class BankInfo(MessageElement):
    """
    Info regarding a bank.
    """

    code: str
    display_name: str
    default_branch_code: str
    rtc_participant: bool
    rtgs_participant: bool
    country_code: str


@dataclass
class WireWithdrawal(MessageElement):
    """
    Wire withdrawal info.
    """

    id: str
    currency: str
    amount: Decimal
    status: str
    created_at: datetime
    wire_bank_account_id: str
