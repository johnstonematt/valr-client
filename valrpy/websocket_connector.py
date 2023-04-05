import json
import time
import threading
import logging
from queue import Queue
from typing import Optional, Dict, List, NoReturn, Generic, TypeVar, Callable

from websocket import WebSocketApp

from valrpy.utils import generate_headers, enforce_type
from valrpy.enums import WebsocketType, WebsocketMessageType
from valrpy.messages import (
    AggregatedOrderbookData,
    FullOrderbookData,
    MarketSummaryData,
    TradeBucketData,
    NewTradeData,
    OpenOrderInfo,
    BalanceUpdateData,
    NewAccountHistoryRecordData,
    NewAccountTradeData,
    InstantOrderCompletedData,
    OrderProcessedData,
    OrderStatusUpdateData,
    FailedCancelOrderData,
    NewPendingReceiveData,
    SendStatusUpdateData,
    MessageData,
    ParsedMessage,
)


logger = logging.getLogger(__name__)

T = TypeVar("T")


class WebsocketPipeline(Generic[T]):
    """
    A wrapper around the WebsocketApp to manage a single websocket 'pipeline'.
    """

    def __init__(
        self,
        url: str,
        queue: Queue[T],
        headers: Dict[str, str],
        opening_messages: List[dict],
        message_formatter: Optional[Callable[[dict], Optional[T]]] = None,
    ) -> None:
        self.queue = queue
        # we use lambdas when passing in the on_something functions because the WebsocketApp expects
        # the function signature to be f(ws: WebsocketApp, x: T) -> None
        self.ws = WebSocketApp(
            url=url,
            header=headers,
            on_open=lambda ws: self._on_open(opening_messages=opening_messages),
            on_error=lambda ws: self._on_error(),
            on_message=lambda ws, message: self._on_message(message=message),
            on_close=self._on_close,
        )
        self._message_formatter = (
            message_formatter
            if message_formatter is not None
            else lambda message: message
        )

    def _on_message(self, message: Optional[str | bytes | dict]) -> None:
        # these if statements are all just parsing the message type to a dict:
        if message is None:
            return

        if isinstance(message, bytes):
            message = message.decode("utf-8")

        if isinstance(message, str):
            message = json.loads(message)

        if not isinstance(message, dict):
            raise TypeError(
                f"Message should be of type dict, but instead received "
                f"{type(message).__name__}: {message}"
            )

        try:
            formatted_message = self._message_formatter(message)

        except Exception as e:
            logger.error(
                f"{type(e).__name__} while formatting message. "
                f"Exception was: {e} "
                f"Message was: {message} "
            )
            logger.exception(e)
            raise

        if formatted_message is not None:
            self.queue.put(formatted_message)

    def _on_open(self, opening_messages: List[dict]) -> None:
        for message in opening_messages:
            self.send_message(message=message)

    def _on_error(self) -> None:
        pass

    def _on_close(self, ws: WebSocketApp) -> None:
        pass

    def _ping_continuously(self) -> NoReturn:
        try:
            while True:
                self.send_message(
                    message={
                        "type": "PING",
                    },
                )
                # the api suggests we ping every 30 seconds, so lets just be a bit conservative with 25:
                time.sleep(25)

        except Exception as e:
            logger.error(f"{type(e).__name__} while pinging continuously:")
            logger.exception(e)
            raise

    def start(self) -> None:
        # run the process:
        threading.Thread(
            target=self._run_websocket,
            daemon=True,
        ).start()

        # sleep a bit before starting the ping, to let the authentication work:
        time.sleep(1)

        # ping continuously:
        threading.Thread(
            target=self._ping_continuously,
            daemon=True,
        ).start()

    def _run_websocket(self) -> None:
        try:
            self.ws.run_forever(
                ping_interval=5,
                ping_timeout=3,
                skip_utf8_validation=True,
            )

        except Exception as e:
            logger.error("Error while running websocket:")
            logger.exception(e)

        finally:
            self._terminate_websocket()

    def send_message(self, message: dict) -> None:
        self.ws.send(
            data=json.dumps(message),
        )

    def _terminate_websocket(self) -> None:
        try:
            self.ws.close()

        except Exception as e:
            logger.error(f"{type(e).__name__} while terminating websocket:")
            logger.exception(e)


class ValrWebsocketConnector:
    """
    Connector for VALR websocket api.
    """

    def __init__(self, api_key: str, api_secret: str) -> None:
        self._api_key = api_key
        self._api_secret = api_secret
        self.base_url = "wss://api.valr.com"
        self.queue: Queue[ParsedMessage] = Queue()

        self._pipelines: Dict[WebsocketType, WebsocketPipeline] = {}
        self._pipeline_lock = threading.Lock()

    def subscribe_to_account(self) -> None:
        self._create_and_start_websocket_pipeline(
            websocket_type=WebsocketType.ACCOUNT,
            opening_messages=[],
        )

    def _message_handler(self, message: dict) -> Optional[ParsedMessage]:
        raw_message_type = message.get("type")
        if raw_message_type is None:
            raise ValueError(f"Message has no type: {message}")

        message_type = WebsocketMessageType(raw_message_type)

        # nothing needs to be done for these types of messages:
        if message_type in (
            WebsocketMessageType.AUTHENTICATED,
            WebsocketMessageType.PING,
            WebsocketMessageType.PONG,
            WebsocketMessageType.SUBSCRIBE,
            WebsocketMessageType.UNSUBSCRIBE,
            WebsocketMessageType.NO_SUBSCRIPTIONS,
        ):
            return

        raw_data = message.get("data")
        if raw_data is None:
            raise ValueError(f"No data in the message: {message}")

        data: MessageData
        match message_type:
            case WebsocketMessageType.AGGREGATED_ORDERBOOK_UPDATE:
                data = AggregatedOrderbookData.from_raw(raw=raw_data)

            case WebsocketMessageType.FULL_ORDERBOOK_UPDATE:
                data = FullOrderbookData.from_raw(raw=raw_data)

            case WebsocketMessageType.MARKET_SUMMARY_UPDATE:
                data = MarketSummaryData.from_raw(raw=raw_data)

            case WebsocketMessageType.NEW_TRADE_BUCKET:
                data = TradeBucketData.from_raw(raw=raw_data)

            case WebsocketMessageType.NEW_TRADE:
                data = NewTradeData.from_raw(raw=raw_data)

            case WebsocketMessageType.OPEN_ORDERS_UPDATE:
                enforce_type(obj=raw_data, obj_type=list)
                data = [OpenOrderInfo.from_raw(raw=raw_order) for raw_order in raw_data]

            case WebsocketMessageType.NEW_ACCOUNT_HISTORY_RECORD:
                data = NewAccountHistoryRecordData.from_raw(raw=raw_data)

            case WebsocketMessageType.BALANCE_UPDATE:
                data = BalanceUpdateData.from_data(raw=raw_data)

            case WebsocketMessageType.NEW_ACCOUNT_TRADE:
                data = NewAccountTradeData.from_raw(raw=raw_data)

            case WebsocketMessageType.INSTANT_ORDER_COMPLETED:
                data = InstantOrderCompletedData.from_raw(raw=raw_data)

            case WebsocketMessageType.ORDER_PROCESSED:
                data = OrderProcessedData.from_raw(raw=raw_data)

            case WebsocketMessageType.ORDER_STATUS_UPDATE:
                data = OrderStatusUpdateData.from_raw(raw=raw_data)

            case WebsocketMessageType.FAILED_CANCEL_ORDER:
                data = FailedCancelOrderData.from_raw(raw=raw_data)

            case WebsocketMessageType.NEW_PENDING_RECEIVE:
                data = NewPendingReceiveData.from_raw(raw=raw_data)

            case WebsocketMessageType.SEND_STATUS_UPDATE:
                data = SendStatusUpdateData.from_raw(raw=raw_data)

            case _:
                raise NotImplementedError(
                    f"No implemented data-format for {message_type} message type."
                )

        return ParsedMessage(
            type=message_type,
            data=data,
        )

    def subscribe_to_market(
        self, event_type: WebsocketMessageType, symbols: List[str]
    ) -> None:
        message = {
            "type": WebsocketMessageType.SUBSCRIBE,
            "subscriptions": [
                {
                    "event": event_type,
                    "pairs": symbols,
                },
            ],
        }
        if self._pipelines.get(WebsocketType.TRADE) is None:
            self._create_and_start_websocket_pipeline(
                websocket_type=WebsocketType.TRADE,
                opening_messages=[message],
            )

        else:
            self._pipelines[WebsocketType.TRADE].send_message(
                message=message,
            )

    def _create_and_start_websocket_pipeline(
        self,
        websocket_type: WebsocketType,
        opening_messages: List[dict],
    ) -> None:
        # technically this could be made faster by having a separate lock for each websocket-type,
        # but I doubt that is necessary
        with self._pipeline_lock:
            if websocket_type in self._pipelines:
                raise ValueError(f"Already have a pipeline for {websocket_type}.")

            headers = generate_headers(
                api_key=self._api_key,
                api_secret=self._api_secret,
                method="GET",
                path=websocket_type.path(),
                body="",
            )
            pipeline = WebsocketPipeline(
                url=f"{self.base_url}{websocket_type.path()}",
                queue=self.queue,
                headers=headers,
                opening_messages=opening_messages,
            )
            pipeline.start()
            self._pipelines[websocket_type] = pipeline
