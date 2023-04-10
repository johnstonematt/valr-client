import json
import logging
from enum import Enum
from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass
from typing import (
    List,
    Optional,
    TypeAlias,
    Any,
    TypeVar,
    get_type_hints,
    Type,
    Dict,
)

from valrpy.constants import TIMEZONE, DATETIME_FORMAT
from valrpy.enums import (
    OrderSide,
    TransactionType,
    WebsocketMessageType,
)


__all__ = [
    "MessageElement",
    "CurrencyInfo",
    "CurrencyPairInfo",
    "AggregatedOrderbook",
    "MarketSummary",
    "TradeBucket",
]

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _timestamp_to_datetime(timestamp: int | float) -> datetime:
    for resolution in (1e0, 1e3, 1e6, 1e9):
        try:
            return datetime.fromtimestamp(timestamp / resolution, tz=TIMEZONE)

        except ValueError as e:
            if "out of range" in str(e):
                continue

            else:
                raise

    else:
        raise ValueError(f"Can't convert timestamp to datetime: {datetime}")


def _to_json(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.isoformat()

    if isinstance(obj, Decimal):
        return str(obj)

    if isinstance(obj, list):
        return [_to_json(obj=item) for item in obj]

    if isinstance(obj, dict):
        return {key: _to_json(obj=val) for key, val in obj.items()}

    if isinstance(obj, MessageElement):
        return _to_json(obj=obj.__dict__)

    return obj


def _parse_to_desired_type(
    obj: Any,
    desired_type: Type[T],
    param_name: str,
) -> T:
    type_name = str(desired_type)
    # check that the param is present:
    if obj is None and not type_name.startswith("typing.Optional"):
        raise TypeError(
            f"Param {param_name} does not accept None. "
            f"Expected type {type_name}, but received None."
        )

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
                    param_name=param_name,
                )
                return result

        if "list" in outer_type_name.lower():
            result = [
                _parse_to_desired_type(
                    obj=item,
                    desired_type=inner_types[0],
                    param_name=param_name,
                )
                for item in obj
            ]
            return result

        raise TypeError(f"Unimplemented desired type: {type_name}")

    # now that we have handled generics, we can do the straight check:
    if isinstance(obj, desired_type):
        return obj

    # handle enums and casing:
    if issubclass(desired_type, Enum):
        if not isinstance(obj, str):
            raise TypeError(f"Can only convert strings to Enum, not {type_name}")

        try:
            return desired_type(obj)

        except ValueError:
            return desired_type(obj.upper().replace("-", "_").replace(" ", "_"))

    # this is to avoid float inaccuracy such as
    # Decimal(0.0001) = 0.000100000000000000004792173602385929598312941379845142364501953125
    if issubclass(desired_type, Decimal) and isinstance(obj, float):
        return Decimal(str(obj))

    if issubclass(desired_type, bool):
        if isinstance(obj, str):
            return obj.lower() == "true"

        else:
            raise TypeError(
                f"Can't convert object of type {type(obj).__name__} to bool."
            )

    if issubclass(desired_type, datetime):
        if isinstance(obj, (int, float, Decimal)):
            return _timestamp_to_datetime(timestamp=obj)

        elif isinstance(obj, str):
            # there is a possibility that a timestamp is still given, but just in string format:
            if obj.isdecimal():
                return _timestamp_to_datetime(timestamp=float(obj))

            # VALR includes a 'Z' at the end of their datetime strings:
            obj = obj.rstrip("Z")

            # this is a strange case where sometimes a datetime will come through like '2023-04-05T14:32:5100',
            # and presumably the last 4 characters mean 51 seconds
            if "." not in obj:
                obj = f"{obj[:19]}.000"

            # VALR typically uses millisecond granularity and then appends a 'Z' at the end,
            # so we remove Z + add '000' to convert to microseconds
            if len(obj) > 26:
                obj = obj[:26]
            else:
                obj += (26 - len(obj)) * "0"

            return datetime.strptime(obj, DATETIME_FORMAT).replace(tzinfo=TIMEZONE)

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

    return desired_type(obj)


def _convert_to_snake_case(camel_case: str) -> str:
    if camel_case.islower():
        return camel_case

    snake_case = ""
    for character in camel_case:
        if character.isalpha() and character.isupper():
            snake_case += f"_{character.lower()}"

        else:
            snake_case += character

    # valr treats subaccount as two words, and I'm pretty sure it's one, so we fix:
    snake_case = snake_case.replace("sub_account", "subaccount")

    return snake_case.lstrip("_")


def _apply_snake_case(camel_dict: Dict[str, Any]) -> Dict[str, Any]:
    snake_case_dict = {}
    for key, val in camel_dict.items():
        snake_key = _convert_to_snake_case(camel_case=key)
        snake_val = _apply_snake_case(camel_dict=val) if isinstance(val, dict) else val
        snake_case_dict[snake_key] = snake_val

    return snake_case_dict


class MessageElement:
    """
    Base class for json parsing into python objects.
    """

    @classmethod
    def from_raw(cls: Type["U"], raw: dict) -> "U":
        try:
            type_hints = get_type_hints(cls.__init__)
            if "return" in type_hints:
                type_hints.pop("return")

            raw = _apply_snake_case(camel_dict=raw)
            # check for no unexpected arguments:
            unexpected_args = [
                arg_name for arg_name in raw.keys() if arg_name not in type_hints
            ]
            if unexpected_args:
                raise ValueError(
                    f"{cls.__name__}.from_raw() received unexpected args: {unexpected_args}"
                )

            parsed_kwargs = {}
            for param_name, desired_type in type_hints.items():
                parsed_kwargs[param_name] = _parse_to_desired_type(
                    obj=raw.get(param_name),
                    desired_type=desired_type,
                    param_name=param_name,
                )

            return cls(**parsed_kwargs)

        except Exception as e:
            logger.error(
                f"{type(e).__name__}({e}) while calling {cls.__name__}.from_raw(), data was: {raw}"
            )
            raise

    def __str__(self) -> str:
        display_dict = _to_json(obj=self)
        return str(display_dict)

    def __repr__(self) -> str:
        return str(self)

    def display(self) -> str:
        display_dict = _to_json(obj=self)
        return json.dumps(obj=display_dict, indent=4)


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
    order_count: Optional[int]


@dataclass
class AggregatedOrderbook(MessageElement):
    """
    Aggregated orderbook.
    """

    asks: List[AggregatedOrderbookLevel]
    bids: List[AggregatedOrderbookLevel]
    last_change: datetime
    sequence_number: int


@dataclass
class MarketSummary(MessageElement):
    """
    Market summary core
    """

    ask_price: Decimal
    bid_price: Decimal
    last_traded_price: Decimal
    previous_close_price: Decimal
    base_volume: Decimal
    quote_volume: Decimal
    high_price: Decimal
    low_price: Decimal
    created: datetime
    change_from_previous: Decimal
    mark_price: Decimal
    # rest request returns 'currencyPair' but websocket returns 'currencyPairSymbol':
    currency_pair: Optional[str]
    currency_pair_symbol: Optional[str]

    def symbol(self) -> str:
        for val in (self.currency_pair, self.currency_pair_symbol):
            if val is not None:
                return val

        raise ValueError(
            "No currency-pair or currency-pair-symbol, maybe the formatting is incorrect?"
        )

    def mid_price(self) -> Decimal:
        return (self.ask_price + self.bid_price) / 2


@dataclass
class TradeBucket(MessageElement):
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
    core currency info
    """

    symbol: str
    decimal_places: int
    is_active: bool
    short_name: str
    long_name: str
    collateral: Optional[bool]
    collateral_weight: Optional[Decimal]
    id: Optional[int]
    payment_reference_field_name: Optional[str]
    # from rest requests, we get 'withdrawDecimalPlaces', but from websocket we get 'supportedWithdrawDecimalPlaces'
    supported_withdraw_decimal_places: Optional[int]
    withdraw_decimal_places: Optional[int]

    def currency_withdraw_decimal_places(self) -> int:
        for val in (
            self.supported_withdraw_decimal_places,
            self.withdraw_decimal_places,
        ):
            if val is not None:
                return val

        raise ValueError(
            f"No currency withdraw decimal places, maybe the message formatting is incorrect."
        )


@dataclass
class CurrencyPairInfo(MessageElement):
    """
    data-format for currency-pair info
    """

    id: Optional[int]
    symbol: str
    base_currency: str | CurrencyInfo
    quote_currency: str | CurrencyInfo
    short_name: str
    exchange: Optional[str]
    active: bool
    tick_size: Decimal
    base_decimal_places: int
    margin_trading_allowed: bool
    min_base_amount: Decimal
    max_base_amount: Decimal
    min_quote_amount: Decimal
    max_quote_amount: Decimal
