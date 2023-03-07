from enum import Enum


__all__ = [
    "TimeInForce",
    "OrderType",
    "OrderSide",
    "TransactionType",
    "TriggerOrderType",
]


class TimeInForce(str, Enum):
    """
    Time-in-force available on VALR
    """

    GTC = "GTC"  # good till cancelled
    FOK = "FOK"  # fill or kill
    IOC = "IOC"  # immediate or cancel


class OrderType(str, Enum):
    """
    Order-types available on VALR
    """

    LIMIT_POST_ONLY = "LIMIT_POST_ONLY"
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SIMPLE = "SIMPLE"
    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"


class OrderSide(str, Enum):
    """
    Order side on VALR.
    """

    BUY = "BUY"
    SELL = "SELL"


class TransactionType(str, Enum):
    """
    Types of transactions in VALR api.
    """

    LIMIT_BUY = "LIMIT_BUY"
    LIMIT_SELL = "LIMIT_SELL"
    MARKET_BUY = "MARKET_BUY"
    MARKET_SELL = "MARKET_SELL"
    SIMPLE_BUY = "SIMPLE_BUY"
    SIMPLE_SELL = "SIMPLE_SELL"
    AUTO_BUY = "AUTO_BUY"
    MAKER_REWARD = "MAKER_REWARD"
    BLOCKCHAIN_RECEIVE = "BLOCKCHAIN_RECEIVE"
    BLOCKCHAIN_SEND = "BLOCKCHAIN_SEND"
    FIAT_DEPOSIT = "FIAT_DEPOSIT"
    FIAT_WITHDRAWAL = "FIAT_WITHDRAWAL"
    REFERRAL_REBATE = "REFERRAL_REBATE"
    REFERRAL_REWARD = "REFERRAL_REWARD"
    PROMOTIONAL_REBATE = "PROMOTIONAL_REBATE"
    INTERNAL_TRANSFER = "INTERNAL_TRANSFER"
    FIAT_WITHDRAWAL_REVERSAL = "FIAT_WITHDRAWAL_REVERSAL"
    PAYMENT_SENT = "PAYMENT_SENT"
    PAYMENT_RECEIVED = "PAYMENT_RECEIVED"
    PAYMENT_REVERSED = "PAYMENT_REVERSED"
    PAYMENT_REWARD = "PAYMENT_REWARD"
    OFF_CHAIN_BLOCKCHAIN_WITHDRAW = "OFF_CHAIN_BLOCKCHAIN_WITHDRAW"
    OFF_CHAIN_BLOCKCHAIN_DEPOSIT = "OFF_CHAIN_BLOCKCHAIN_DEPOSIT"
    SIMPLE_SWAP_BUY = "SIMPLE_SWAP_BUY"
    SIMPLE_SWAP_SELL = "SIMPLE_SWAP_SELL"
    SIMPLE_SWAP_FAILURE_REVERSAL = "SIMPLE_SWAP_FAILURE_REVERSAL"


class TriggerOrderType(str, Enum):
    """
    Types of trigger orders available on VALR
    """

    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"


class OrderInstruction(str, Enum):
    """
    Types of order-actions available on VALR
    """

    PLACE_MARKET = "PLACE_MARKET"
    PLACE_LIMIT = "PLACE_LIMIT"
    PLACE_STOP_LIMIT = "PLACE_STOP_LIMIT"
    CANCEL_ORDER = "CANCEL_ORDER"
