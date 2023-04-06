import os
import time
from decimal import Decimal

from dotenv import load_dotenv

from valrpy.enums import OrderSide, OrderType
from valrpy.rest_connector import ValrRestConnector
from valrpy.messages import *


load_dotenv("../.env.local")


connector = ValrRestConnector(
    api_key=os.getenv("VALR_API_KEY"),
    api_secret=os.getenv("VALR_API_SECRET"),
)

SYMBOL = "BTCZAR"


def _assert_listed_type(obj: list, desired_type: type) -> None:
    assert isinstance(obj, list)
    for item in obj:
        assert isinstance(item, desired_type)


def test_place_market_order() -> None:
    buy_order_id = connector.place_market_order(
        symbol=SYMBOL,
        quote_amount=10,
        side=OrderSide.BUY,
    )
    assert isinstance(buy_order_id, str)

    sell_order_id = connector.place_market_order(
        symbol=SYMBOL,
        quote_amount=10,
        side=OrderSide.SELL,
    )
    assert isinstance(sell_order_id, str)

    # sleep a bit to make sure:
    time.sleep(1)

    for side, order_id in [
        (OrderSide.BUY, buy_order_id),
        (OrderSide.SELL, sell_order_id),
    ]:
        order = connector.get_old_order_summary(
            order_id=order_id,
        )
        assert isinstance(order, HistoricalOrder)
        assert order.order_type == OrderType.MARKET
        assert order.order_side == side
        assert order.order_id == order_id


def test_place_limit_order() -> None:
    market_summary = connector.get_symbol_market_summary(symbol=SYMBOL)
    assert isinstance(market_summary, MarketSummaryData)

    order_id = connector.place_limit_order(
        symbol=SYMBOL,
        side=OrderSide.BUY,
        quantity=0.0001,
        price=round(Decimal(0.9) * market_summary.bid_price),
    )
    assert isinstance(order_id, str)

    # give it a second:
    time.sleep(1)

    open_orders = connector.get_open_orders()
    assert order_id in [open_order.order_id for open_order in open_orders]

    order_status = connector.get_order_status(
        symbol=SYMBOL,
        order_id=order_id,
    )
    assert isinstance(order_status, OrderStatus)
    assert order_status.order_id == order_id

    connector.cancel_order(
        symbol=SYMBOL,
        order_id=order_id,
    )

    # give it a second:
    time.sleep(1)

    open_orders = connector.get_open_orders()
    assert order_id not in [open_order.order_id for open_order in open_orders]
