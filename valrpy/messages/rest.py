from decimal import Decimal
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List

from valrpy.enums import OrderSide, OrderType, TimeInForce
from valrpy.messages.core import (
    MessageElement,
    CurrencyPairInfo,
)


__all__ = [
    "RestOrderbookOrder",
    "RestFullOrderbook",
    "RestOpenOrderInfo",
    "PairOrderTypes",
    "HistoricalMarketTrade",
    "ServerTime",
    "WithdrawalAddress",
    "ApiKeyInfo",
    "SubaccountInfo",
    "WalletBalance",
    "SubaccountBalance",
    "HistoricalAccountTrade",
    "WhitelistedAddress",
    "CurrencyWithdrawalInfo",
    "WithdrawalStatus",
    "HistoricalDeposit",
    "HistoricalWithdrawal",
    "BankAccountDetail",
    "WireWithdrawal",
    "OrderStatus",
    "RestOpenOrder",
    "HistoricalOrder",
]


@dataclass
class RestOrderbookOrder(MessageElement):
    """
    Order-summary in an orderbook.
    """

    side: OrderSide
    quantity: Decimal
    price: Decimal
    currency_pair: str
    id: str
    position_at_price: int


@dataclass
class RestFullOrderbook(MessageElement):
    """
    Data-format for full orderbook snapshot.
    """

    last_change: datetime
    asks: List[RestOrderbookOrder]
    bids: List[RestOrderbookOrder]
    sequence_number: int
    checksum: Optional[int]


@dataclass
class RestOpenOrderInfo(MessageElement):
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
    allowed_ip_address_cidr: Optional[str]
    allowed_withdraw_address_list: Optional[List[WithdrawalAddress]]
    is_subaccount: bool


@dataclass
class SubaccountInfo(MessageElement):
    """
    Subaccount info.
    """

    label: str
    id: int


@dataclass
class WalletBalance(MessageElement):
    """
    Wallet balance.
    """

    currency: str
    available: Decimal
    reserved: Decimal
    total: Decimal
    updated_at: Optional[datetime]
    lend_reserved: Decimal
    borrow_reserved: Decimal
    borrowed_amount: Decimal


@dataclass
class SubaccountBalance(MessageElement):
    """
    Subaccount balance.
    """

    account: SubaccountInfo
    balances: List[WalletBalance]


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


@dataclass
class OrderStatus(MessageElement):
    """
    Order status.
    """

    order_id: str
    order_status_type: str
    currency_pair: str
    original_price: Decimal
    remaining_quantity: Decimal
    original_quantity: Decimal
    order_side: OrderSide
    order_type: OrderType
    failed_reason: Optional[str]
    order_updated_at: datetime
    order_created_at: datetime
    customer_order_id: Optional[str]
    time_in_force: TimeInForce


@dataclass
class RestOpenOrder(MessageElement):
    """
    Data format when rest polling open orders
    """

    order_id: str
    side: OrderSide
    remaining_quantity: Decimal
    price: Decimal
    currency_pair: str
    created_at: datetime
    original_quantity: Decimal
    filled_percentage: Decimal
    stop_price: Optional[Decimal]
    updated_at: datetime
    status: str
    type: OrderType
    time_in_force: TimeInForce


@dataclass
class HistoricalOrder(MessageElement):
    """
    Data format for historical orders
    """

    order_id: str
    order_status_type: str
    currency_pair: str
    average_price: Decimal
    original_price: Decimal
    remaining_quantity: Decimal
    original_quantity: Decimal
    total: Decimal
    total_fee: Decimal
    fee_currency: str
    order_side: OrderSide
    order_type: OrderType
    failed_reason: Optional[str]
    order_updated_at: datetime
    order_created_at: datetime
    time_in_force: TimeInForce
