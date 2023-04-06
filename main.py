import threading

from valrpy.websocket_connector import ValrWebsocketConnector
from valrpy.rest_connector import ValrRestConnector


class ValrBot:

    def __init__(self, api_key, api_secret):
        self.ws_connector = ValrWebsocketConnector(
            api_key, api_secret
        )
        self.rest_connector = ValrRestConnector(
            api_key, api_secret
        )

    def run(self) -> None:
        self.ws_connector.subscribe_to_market()
        self.ws_connector.subscribe_to_account()
        while True:
            latest_message = self.ws_connector.queue.get()
            self.process_message(message=latest_message)

    def place_order(self):
        self.rest_connector.place_limit_order()
        threading.Thread(self.confirm_order).start()

    def confirm_order(self):
        if order not in websocket:
            self.rest_connector.get_open_orders()

    def process_message(self, message):
        self.rest_connector.place_limit_order()
