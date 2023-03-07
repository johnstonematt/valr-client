from typing import TypedDict


class OrderbookEntry(TypedDict):
    """
    An entry in an orderbook.
    """

    side: str
    quantity: str
    price: str
