from enum import Enum


__all__ = [
    "TimeInForce",
    "OrderType",
    "OrderSide",
    "TransactionType",
    "TriggerOrderType",
    "WebsocketType",
    "WebsocketMessageType",
]


class BaseStrEnum(str, Enum):
    """
    Base class for str enums.
    """

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return str(self)


class TimeInForce(BaseStrEnum):
    """
    Time-in-force available on VALR
    """

    GTC = "GTC"  # good till cancelled
    FOK = "FOK"  # fill or kill
    IOC = "IOC"  # immediate or cancel


class OrderType(BaseStrEnum):
    """
    Order-types available on VALR
    """

    LIMIT_POST_ONLY = "LIMIT_POST_ONLY"
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SIMPLE = "SIMPLE"
    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"


class OrderSide(BaseStrEnum):
    """
    Order side on VALR.
    """

    BUY = "BUY"
    SELL = "SELL"


class TransactionType(BaseStrEnum):
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


class TriggerOrderType(BaseStrEnum):
    """
    Types of trigger orders available on VALR
    """

    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"


class OrderInstruction(BaseStrEnum):
    """
    Types of order-actions available on VALR
    """

    PLACE_MARKET = "PLACE_MARKET"
    PLACE_LIMIT = "PLACE_LIMIT"
    PLACE_STOP_LIMIT = "PLACE_STOP_LIMIT"
    CANCEL_ORDER = "CANCEL_ORDER"


class WebsocketType(BaseStrEnum):
    """
    Type of websockets on VALR
    """

    ACCOUNT = "ACCOUNT"
    TRADE = "TRADE"

    def path(self) -> str:
        match self:
            case WebsocketType.ACCOUNT:
                return "/ws/account"

            case WebsocketType.TRADE:
                return "/ws/trade"

            case _:
                raise NotImplementedError(
                    f"No path for the following websocket-type: {self}"
                )


class WebsocketMessageType(BaseStrEnum):
    """
    Type of websocket messages from VALR
    """

    # general:
    AUTHENTICATED = "AUTHENTICATED"
    PING = "PING"
    PONG = "PONG"
    SUBSCRIBE = "SUBSCRIBE"
    UNSUBSCRIBE = "UNSUBSCRIBE"
    SUBSCRIBED = "SUBSCRIBED"
    UNSUBSCRIBED = "UNSUBSCRIBED"
    NO_SUBSCRIPTIONS = "NO_SUBSCRIPTIONS"
    # account updates:
    NEW_ACCOUNT_HISTORY_RECORD = "NEW_ACCOUNT_HISTORY_RECORD"
    BALANCE_UPDATE = "BALANCE_UPDATE"
    NEW_ACCOUNT_TRADE = "NEW_ACCOUNT_TRADE"
    INSTANT_ORDER_COMPLETED = "INSTANT_ORDER_COMPLETED"
    OPEN_ORDERS_UPDATE = "OPEN_ORDERS_UPDATE"
    ORDER_PROCESSED = "ORDER_PROCESSED"
    ORDER_STATUS_UPDATE = "ORDER_STATUS_UPDATE"
    FAILED_CANCEL_ORDER = "FAILED_CANCEL_ORDER"
    NEW_PENDING_RECEIVE = "NEW_PENDING_RECEIVE"
    SEND_STATUS_UPDATE = "SEND_STATUS_UPDATE"
    # trade updates:
    AGGREGATED_ORDERBOOK_UPDATE = "AGGREGATED_ORDERBOOK_UPDATE"
    FULL_ORDERBOOK_UPDATE = "FULL_ORDERBOOK_UPDATE"
    MARKET_SUMMARY_UPDATE = "MARKET_SUMMARY_UPDATE"
    NEW_TRADE_BUCKET = "NEW_TRADE_BUCKET"
    NEW_TRADE = "NEW_TRADE"
    MARK_PRICE_UPDATE = "MARK_PRICE_UPDATE"

    def has_data(self) -> bool:
        match self:
            case (
                WebsocketMessageType.AUTHENTICATED
                | WebsocketMessageType.PING
                | WebsocketMessageType.PONG
                | WebsocketMessageType.SUBSCRIBE
                | WebsocketMessageType.UNSUBSCRIBE
                | WebsocketMessageType.SUBSCRIBED
                | WebsocketMessageType.UNSUBSCRIBED
                | WebsocketMessageType.NO_SUBSCRIPTIONS
            ):
                return False

            case _:
                return True

    def websocket_type(self) -> WebsocketType:
        match self:
            case (
                WebsocketMessageType.OPEN_ORDERS_UPDATE
                | WebsocketMessageType.BALANCE_UPDATE
            ):
                return WebsocketType.ACCOUNT

            case (
                WebsocketMessageType.AGGREGATED_ORDERBOOK_UPDATE
                | WebsocketMessageType.FULL_ORDERBOOK_UPDATE
                | WebsocketMessageType.MARKET_SUMMARY_UPDATE
                | WebsocketMessageType.NEW_TRADE_BUCKET
                | WebsocketMessageType.NEW_TRADE
                | WebsocketMessageType.MARKET_SUMMARY_UPDATE
            ):
                return WebsocketType.TRADE

            case _:
                raise NotImplementedError(
                    f"No websocket-type for the following message-type: {self}"
                )
