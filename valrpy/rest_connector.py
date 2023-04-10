import json
from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Union

from requests import Session, Request, JSONDecodeError

from valrpy.enums import (
    TransactionType,
    OrderSide,
    OrderType,
    TimeInForce,
    TriggerOrderType,
    ExchangeStatus,
)
from valrpy.constants import Number
from valrpy.utils import generate_headers, RestException, datetime_to_milliseconds
from valrpy.messages.core import (
    AggregatedOrderbook,
    CurrencyInfo,
    CurrencyPairInfo,
    MarketSummary,
)
from valrpy.messages.rest import (
    RestFullOrderbook,
    PairOrderTypes,
    HistoricalMarketTrade,
    ServerTime,
    ApiKeyInfo,
    SubaccountInfo,
    SubaccountBalance,
    WalletBalance,
    HistoricalAccountTrade,
    WhitelistedAddress,
    CurrencyWithdrawalInfo,
    WithdrawalStatus,
    HistoricalDeposit,
    HistoricalWithdrawal,
    BankAccountDetail,
    WireWithdrawal,
    OrderStatus,
    RestOpenOrder,
    HistoricalOrder,
)


__all__ = [
    "ValrRestConnector",
]


class ValrRestConnector:
    """
    Client for accessing public api endpoints.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        subaccount: Optional[str] = None,
    ) -> None:
        self._url = "https://api.valr.com/v1"
        self._api_key = api_key
        self._api_secret = api_secret
        self._subaccount = subaccount

        self._session = Session()

    # ========== REST HELPER METHODS ===========:

    def _make_request(
        self,
        method: str,
        endpoint: str,
        auth: bool,
        **kwargs,
    ) -> Optional[dict | list]:
        request = Request(
            method=method,
            url=f"{self._url}/{endpoint}",
            **kwargs,
        )
        if auth:
            self._sign_request(
                request=request,
                endpoint=endpoint,
            )

        response = self._session.send(request.prepare())
        try:
            response_json: Union[dict | list] = response.json(
                parse_float=lambda x: Decimal(x)
            )
            if isinstance(response_json, list):
                return response_json

            if isinstance(response_json, dict):
                error_code = response_json.get("code")
                if error_code:
                    raise RestException(response_json)

                else:
                    return response_json

            # if this code runs, we received an unrecognised type
            raise TypeError(
                f"Unrecognised response type: {type(response_json).__name__}. "
                f"Response was: {response_json}"
            )

        except (json.JSONDecodeError, JSONDecodeError):
            response.raise_for_status()
            # when sending delete requests, we sometimes get a 202 status code in which everything went fine,
            # but it still raises a json decode error, so in that case we just return nothing
            if response.status_code in (200, 202) and method == "DELETE":
                return
            raise

    def _sign_request(self, request: Request, endpoint: str) -> None:
        if self._api_key is None or self._api_secret is None:
            raise ValueError(
                "Must provide an api-key and an api-secret in order to sign a request. "
                "Without an api-key, you can only hit public endpoints"
            )

        if request.method in ("GET", "POST"):
            payload = "" if request.json is None else request.json

        else:
            payload = request.json

        headers = generate_headers(
            api_key=self._api_key,
            api_secret=self._api_secret,
            method=request.method,
            path=f"/v1/{endpoint}",
            body=payload,
            subaccount_id=self._subaccount,
        )
        for header_name, header_val in headers.items():
            request.headers[header_name] = header_val

    def _get(
        self, endpoint: str, auth: bool, params: Optional[dict] = None
    ) -> dict | list:
        response = self._make_request(
            method="GET",
            endpoint=endpoint,
            auth=auth,
            json=params,
        )
        return response

    def _post(self, endpoint: str, auth: bool, params: Optional[dict] = None) -> dict:
        response = self._make_request(
            method="POST",
            endpoint=endpoint,
            auth=auth,
            json=params,
        )
        return response

    def _delete(self, endpoint: str, auth: bool, params: Optional[dict] = None) -> dict:
        response = self._make_request(
            method="DELETE",
            endpoint=endpoint,
            auth=auth,
            json=params,
        )
        return response

    # ========== PUBLIC ENDPOINTS ===========:

    def get_aggregated_orderbook(self, symbol: str) -> AggregatedOrderbook:
        orderbook_data = self._get(
            endpoint=f"public/{symbol}/orderbook",
            auth=False,
        )
        return AggregatedOrderbook.from_raw(raw=orderbook_data)

    def get_full_orderbook(self, symbol: str) -> RestFullOrderbook:
        orderbook = self._get(
            endpoint=f"public/{symbol}/orderbook/full",
            auth=False,
        )
        # return orderbook
        return RestFullOrderbook.from_raw(raw=orderbook)

    def get_currencies(self) -> List[CurrencyInfo]:
        currencies = self._get(
            endpoint="public/currencies",
            auth=False,
        )
        return [CurrencyInfo.from_raw(raw=raw_info) for raw_info in currencies]

    def get_currency_pairs(self) -> List[CurrencyPairInfo]:
        pairs = self._get(
            endpoint="public/pairs",
            auth=False,
        )
        return [CurrencyPairInfo.from_raw(raw=raw_pair) for raw_pair in pairs]

    def get_all_order_types(self) -> List[PairOrderTypes]:
        order_types = self._get(
            endpoint="public/ordertypes",
            auth=False,
        )
        return [PairOrderTypes.from_raw(raw=raw_types) for raw_types in order_types]

    def get_symbol_order_types(self, symbol: str) -> List[OrderType]:
        order_types = self._get(
            endpoint=f"public/{symbol}/ordertypes",
            auth=False,
        )
        # return order_types
        return [OrderType(order_type.upper()) for order_type in order_types]

    def get_all_market_summaries(self) -> List[MarketSummary]:
        market_summaries = self._get(
            endpoint="public/marketsummary",
            auth=False,
        )
        return [
            MarketSummary.from_raw(raw=raw_summary) for raw_summary in market_summaries
        ]

    def get_symbol_market_summary(self, symbol: str) -> MarketSummary:
        market_summary = self._get(
            endpoint=f"public/{symbol}/marketsummary",
            auth=False,
        )
        return MarketSummary.from_raw(raw=market_summary)

    def get_trade_history(
        self,
        symbol: str,
        skip: int = 0,
        limit: int = 10,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[HistoricalMarketTrade]:
        params = {
            "skip": skip,
            "limit": limit,
            "startTime": datetime_to_milliseconds(dt=start_time),
            "endTime": datetime_to_milliseconds(dt=end_time),
        }
        trade_history = self._get(
            endpoint=f"public/{symbol}/trades",
            params=params,
            auth=False,
        )
        return [
            HistoricalMarketTrade.from_raw(raw=raw_trade) for raw_trade in trade_history
        ]

    def get_server_time(self) -> ServerTime:
        server_time = self._get(
            endpoint="public/time",
            auth=False,
        )
        return ServerTime.from_raw(raw=server_time)

    def get_exchange_status(self) -> ExchangeStatus:
        exchange_status = self._get(
            endpoint="public/status",
            auth=False,
        )
        return ExchangeStatus(exchange_status["status"].upper().replace("-", "_"))

    # ========== ACCOUNT INFO ==========:

    def get_current_api_key_info(self) -> ApiKeyInfo:
        info = self._get(
            endpoint="account/api-keys/current",
            auth=True,
        )
        return ApiKeyInfo.from_raw(raw=info)

    def get_subaccounts(self) -> List[SubaccountInfo]:
        subaccounts = self._get(
            endpoint="account/subaccounts",
            auth=True,
        )
        return [SubaccountInfo(**sub_info) for sub_info in subaccounts]

    def get_non_zero_balances(self) -> List[SubaccountBalance]:
        balances = self._get(
            endpoint="account/balances/all",
            auth=True,
        )
        return [SubaccountBalance.from_raw(raw=balance) for balance in balances]

    def register_subaccount(self, label: str) -> int:
        """
        Register a new subaccount.

        :param label: The subaccount label.
        :return: The subaccount ID.
        """
        params = {
            "label": label,
        }
        response = self._post(
            endpoint="account/subaccount",
            params=params,
            auth=True,
        )
        return int(response["id"])

    def make_internal_transfer(
        self,
        from_id: str,
        to_id: str,
        symbol: str,
        amount: Number,
    ) -> dict:
        params = {
            "fromId": from_id,
            "toId": to_id,
            "currencyCode": symbol,
            "amount": str(amount),
        }
        response = self._post(
            endpoint="account/subaccounts/transfer",
            params=params,
            auth=True,
        )
        return response

    def get_wallet_balances(self) -> List[WalletBalance]:
        balances = self._get(
            endpoint="account/balances",
            auth=True,
        )
        return [WalletBalance.from_raw(raw=raw_balance) for raw_balance in balances]

    def get_transaction_history(
        self,
        skip: int = 0,
        limit: int = 200,
        currency: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        transaction_types: Optional[List[TransactionType]] = None,
    ) -> List[dict]:
        params = {
            "skip": skip,
            "limit": limit,
            "currency": currency,
            "startTime": datetime_to_milliseconds(dt=start_time),
            "endTime": datetime_to_milliseconds(dt=end_time),
            "transactionTypes": ",".join(transaction_types)
            if transaction_types is not None
            else None,
        }
        transactions = self._get(
            endpoint="account/transactionhistory",
            params=params,
            auth=True,
        )
        return transactions

    def get_symbol_trade_history(
        self, symbol: str, limit: int = 10
    ) -> List[HistoricalAccountTrade]:
        params = {
            "limit": limit,
        }
        trade_history = self._get(
            endpoint=f"account/{symbol}/tradehistory",
            params=params,
            auth=True,
        )
        return [
            HistoricalAccountTrade.from_raw(raw=raw_trade)
            for raw_trade in trade_history
        ]

    # ========== WALLET INFO ==========:

    def get_currency_deposit_address(self, currency: str) -> str:
        response = self._get(
            endpoint=f"wallet/crypto/{currency}/deposit/address",
            auth=True,
        )
        return str(response["address"])

    def get_whitelisted_withdrawal_address_book(
        self, currency: Optional[str] = None
    ) -> List[WhitelistedAddress]:
        endpoint = (
            "wallet/crypto/address-book"
            if currency is None
            else f"wallet/crypto/address-book/{currency}"
        )
        address_book = self._get(
            endpoint=endpoint,
            auth=True,
        )
        return [WhitelistedAddress.from_raw(raw=raw_info) for raw_info in address_book]

    def get_currency_withdrawal_info(self, currency: str) -> CurrencyWithdrawalInfo:
        info = self._get(
            endpoint=f"wallet/crypto/{currency}/withdraw",
            auth=True,
        )
        return CurrencyWithdrawalInfo.from_raw(raw=info)

    def make_crypto_withdrawal(
        self, currency: str, amount: Number, address: str
    ) -> str:
        params = {
            "amount": str(amount),
            "address": address,
        }
        response = self._post(
            endpoint=f"wallet/crypto/{currency}/withdraw",
            params=params,
            auth=True,
        )
        return response["id"]

    def get_withdrawal_status(
        self, currency: str, withdrawal_id: str
    ) -> WithdrawalStatus:
        status = self._get(
            endpoint=f"wallet/crypto/{currency}/withdraw/{withdrawal_id}",
            auth=True,
        )
        return WithdrawalStatus.from_raw(raw=status)

    def get_deposit_history(
        self, currency: str, skip: int = 0, limit: int = 10
    ) -> List[HistoricalDeposit]:
        params = {
            "skip": skip,
            "limit": limit,
        }
        history = self._get(
            endpoint=f"wallet/crypto/{currency}/receive/history",
            params=params,
            auth=True,
        )
        return [HistoricalDeposit.from_raw(raw=raw_deposit) for raw_deposit in history]

    def get_withdrawal_history(
        self, currency: str, skip: int = 0, limit: int = 10
    ) -> List[HistoricalWithdrawal]:
        params = {
            "skip": skip,
            "limit": limit,
        }
        history = self._get(
            endpoint=f"wallet/crypto/{currency}/withdraw/history",
            params=params,
            auth=True,
        )
        return [
            HistoricalWithdrawal.from_raw(raw=raw_withdrawal)
            for raw_withdrawal in history
        ]

    def get_associated_bank_accounts(self, currency: str) -> List[BankAccountDetail]:
        accounts = self._get(
            endpoint=f"wallet/fiat/{currency}/accounts",
            auth=True,
        )
        return [BankAccountDetail.from_raw(raw=account) for account in accounts]

    def get_deposit_reference(self, currency: str) -> str:
        reference = self._get(
            endpoint=f"wallet/fiat/{currency}/deposit/reference",
            auth=True,
        )
        return str(reference["reference"])

    def make_fiat_withdrawal(
        self, currency: str, amount: Number, bank_account_id: str, fast: bool
    ) -> str:
        params = {
            "amount": str(amount),
            "linkedBankAccountId": bank_account_id,
            "fast": fast,
        }
        response = self._get(
            endpoint=f"wallet/fiat/{currency}/withdrawal",
            params=params,
            auth=True,
        )
        return response["id"]

    def get_wire_accounts(self) -> List[dict]:
        accounts = self._get(
            endpoint="wire/accounts",
            auth=True,
        )
        return accounts

    def make_wire_withdrawal(self, amount: str, wire_account_id: str) -> WireWithdrawal:
        params = {
            "amount": amount,
            "wireBankAccountId": wire_account_id,
        }
        response = self._post(
            endpoint="wire/withdrawals",
            params=params,
            auth=True,
        )
        return WireWithdrawal.from_raw(raw=response)

    # ========== SIMPLE TRADE ENDPOINTS ==========:

    def get_simple_trade_quote(
        self, symbol: str, pay_currency: str, pay_amount: Number, side: OrderSide
    ) -> dict:
        params = {
            "payInCurrency": pay_currency,
            "payAmount": str(pay_amount),
            "side": side,
        }
        response = self._post(
            endpoint=f"simple/{symbol}/quote",
            params=params,
            auth=True,
        )
        return response

    def submit_simple_order(
        self, symbol: str, pay_currency: str, pay_amount: Number, side: OrderSide
    ) -> dict:
        params = {
            "payInCurrency": pay_currency,
            "payAmount": str(pay_amount),
            "side": side,
        }
        response = self._post(
            endpoint=f"simple/{symbol}/quote",
            params=params,
            auth=True,
        )
        return response

    def get_simple_order_status(self, symbol: str, order_id: str) -> dict:
        status = self._get(
            endpoint=f"simple/{symbol}/order/{order_id}",
            auth=True,
        )
        return status

    # ========== PAYMENT ENDPOINTS ==========:

    def make_new_payment(
        self,
        currency: str,
        amount: Number,
        recipient: str,
        recipient_note: Optional[str] = None,
        sender_note: Optional[str] = None,
        anonymous: bool = False,
    ) -> dict:
        recipient_tag = (
            "recipientCellNumber"
            if recipient.lstrip("+").isdecimal()
            else "recipientEmail"
            if "@" in recipient
            else "recipientPayId"
        )
        params = {
            "currency": currency,
            "amount": str(amount),
            recipient_tag: recipient,
            "recipientNote": recipient_note,
            "senderNote": sender_note,
            "anonymous": anonymous,
        }
        response = self._post(
            endpoint="pay",
            params=params,
            auth=True,
        )
        return response

    def get_payment_limits(self, currency: str) -> dict:
        params = {
            "currency": currency,
        }
        response = self._get(
            endpoint=f"pay/limits",
            params=params,
            auth=True,
        )
        return response

    def get_account_pay_id(self) -> dict:
        pay_id = self._get(
            endpoint="pay/payid",
            auth=True,
        )
        return pay_id

    def get_payment_history(self) -> List[dict]:
        history = self._get(
            endpoint="pay/history",
            auth=True,
        )
        return history

    def get_payment_details(self, payment_identifier: str) -> dict:
        details = self._get(
            endpoint=f"pay/identifier/{payment_identifier}",
            auth=True,
        )
        return details

    def get_payment_status(self, transaction_id: str) -> dict:
        status = self._get(
            endpoint=f"pay/transactionid/{transaction_id}",
            auth=True,
        )
        return status

    # ========== EXCHANGE TRADING ENDPOINTS ==========:

    def place_limit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: Number,
        price: Number,
        post_only: Optional[bool] = None,
        client_order_id: Optional[int] = None,
        time_in_force: TimeInForce = TimeInForce.GTC,
    ) -> str:
        params = {
            "side": side,
            "quantity": str(quantity),
            "price": str(price),
            "pair": symbol,
            "postOnly": post_only,
            "customerOrderId": client_order_id,
            "timeInForce": time_in_force,
        }
        response = self._post(
            endpoint="orders/limit",
            params=params,
            auth=True,
        )
        return str(response["id"])

    def place_market_order(
        self,
        symbol: str,
        side: OrderSide,
        base_amount: Optional[Number] = None,
        quote_amount: Optional[Number] = None,
        client_order_id: Optional[int] = None,
    ) -> str:
        if (base_amount is None and quote_amount is None) or (
            base_amount is not None and quote_amount is not None
        ):
            raise ValueError(
                f"Must provide either a quote amount or a base amount, not both."
            )

        if base_amount is not None:
            amount_key, amount = "baseAmount", base_amount

        else:
            amount_key, amount = "quoteAmount", quote_amount

        params = {
            "pair": symbol,
            "side": side,
            amount_key: amount,
            "customerOrderId": client_order_id,
        }
        response = self._post(
            endpoint="orders/market",
            params=params,
            auth=True,
        )
        return str(response["id"])

    def place_trigger_limit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: Number,
        price: Number,
        trigger_price: Number,
        order_type: TriggerOrderType,
        client_order_id: Optional[int] = None,
        time_in_force: TimeInForce = TimeInForce.GTC,
    ) -> str:
        params = {
            "pair": symbol,
            "side": side,
            "quantity": str(quantity),
            "price": str(price),
            "stopPrice": str(trigger_price),
            "type": order_type,
            "customerOrderId": client_order_id,
            "timeInForce": time_in_force,
        }
        response = self._post(
            endpoint="orders/stop/limit",
            params=params,
            auth=True,
        )
        return str(response["id"])

    def get_order_status(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        client_order_id: Optional[int] = None,
    ) -> OrderStatus:
        if (order_id is None and client_order_id is None) or (
            order_id is not None and client_order_id is not None
        ):
            raise ValueError(f"Must provide either an order-id or a client-order-id.")

        endpoint = (
            f"orders/{symbol}/orderid/{order_id}"
            if order_id is not None
            else f"orders/{symbol}/customerorderid/{client_order_id}"
        )
        status = self._get(
            endpoint=endpoint,
            auth=True,
        )
        return OrderStatus.from_raw(raw=status)

    def get_open_orders(self) -> List[RestOpenOrder]:
        open_orders = self._get(
            endpoint="orders/open",
            auth=True,
        )
        return [RestOpenOrder.from_raw(raw=raw_order) for raw_order in open_orders]

    def get_order_history(
        self, skip: int = 0, limit: Optional[int] = None
    ) -> List[HistoricalOrder]:
        params = {
            "skip": skip,
            "limit": limit,
        }
        order_history = self._get(
            endpoint="orders/history",
            params=params,
            auth=True,
        )
        return [HistoricalOrder.from_raw(raw=raw_order) for raw_order in order_history]

    def get_old_order_summary(
        self,
        order_id: Optional[str] = None,
        client_order_id: Optional[int] = None,
    ) -> HistoricalOrder:
        if (order_id is None and client_order_id is None) or (
            order_id is not None and client_order_id is not None
        ):
            raise ValueError(f"Must provide either an order-id or a client-order-id.")

        endpoint = (
            f"orders/history/summary/orderid/{order_id}"
            if order_id is not None
            else f"orders/history/summary/customerorderid/{client_order_id}"
        )
        summary = self._get(
            endpoint=endpoint,
            auth=True,
        )
        return HistoricalOrder.from_raw(raw=summary)

    def get_old_order_details(
        self,
        order_id: Optional[str] = None,
        client_order_id: Optional[int] = None,
    ) -> dict:
        if (order_id is None and client_order_id is None) or (
            order_id is not None and client_order_id is not None
        ):
            raise ValueError(f"Must provide either an order-id or a client-order-id.")

        endpoint = (
            f"orders/history/detail/orderid/{order_id}"
            if order_id is not None
            else f"orders/history/detail/customerorderid/{client_order_id}"
        )
        details = self._get(
            endpoint=endpoint,
            auth=True,
        )
        return details

    def cancel_order(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        client_order_id: Optional[int] = None,
    ) -> dict:
        if (order_id is None and client_order_id is None) or (
            order_id is not None and client_order_id is not None
        ):
            raise ValueError(f"Must provide either an order-id or a client-order-id.")

        id_tag = "orderId" if order_id is not None else "customerOrderId"
        params = {
            "pair": symbol,
            id_tag: order_id if order_id is not None else client_order_id,
        }
        response = self._delete(
            endpoint="orders/order",
            params=params,
            auth=True,
        )
        return response

    def cancel_all_open_orders(self, symbol: Optional[str] = None) -> dict:
        endpoint = "orders" if symbol is None else f"orders/{symbol}"
        response = self._delete(
            endpoint=endpoint,
            auth=True,
        )
        return response
