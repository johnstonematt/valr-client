import json
import time
from typing import List, Optional

from requests import Session, Request

from valrpy.enums import (
    TransactionType,
    OrderSide,
    TimeInForce,
    TriggerOrderType,
)
from valrpy.utils import request_signature


class ValrClient:
    """
    Client for accessing public api endpoints.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._url = "https://api.valr.com/v1"
        self._api_key = api_key

        self._session = Session()

    # ========== REST HELPER METHODS ===========:

    def _make_request(
        self,
        method: str,
        endpoint: str,
        auth: bool,
        **kwargs,
    ) -> dict | list:
        request = Request(
            method=method,
            url=f"{self._url}/{endpoint}",
            **kwargs,
        )
        if auth:
            self._sign_request(request=request)

        response = self._session.send(request.prepare())
        try:
            return response.json()

        except json.JSONDecodeError:
            response.raise_for_status()
            raise

    def _sign_request(self, request: Request) -> None:
        if self._api_key is None:
            raise ValueError(
                "Must provide an api-key in order to sign a request. "
                "Without an api-key, you can only hit public endpoints"
            )

        timestamp = round(1e3 * time.time())
        signature = request_signature(
            api_key_secret=self._api_key,
            method=request.method,
            path=request.url,
            body=request.json,
            timestamp=timestamp,
        )
        request.headers["X-VALR-API-KEY"] = self._api_key
        request.headers["X-VALR-SIGNATURE"] = signature
        request.headers["X-VALR-TIMESTAMP"] = timestamp

    def _get(
        self, endpoint: str, auth: bool, params: Optional[dict] = None
    ) -> dict | list:
        response = self._make_request(
            method="GET",
            endpoint=endpoint,
            auth=auth,
            params=params,
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

    def get_orderbook(self, symbol: str) -> dict:
        orderbook = self._get(
            endpoint=f"public/{symbol}/orderbook",
            auth=False,
        )
        return orderbook

    def get_full_orderbook(self, symbol: str) -> dict:
        orderbook = self._get(
            endpoint=f"public/{symbol}/orderbook/full",
            auth=False,
        )
        return orderbook

    def get_currencies(self) -> List[dict]:
        currencies = self._get(
            endpoint="public/currencies",
            auth=False,
        )
        return currencies

    def get_all_order_types(self) -> List[dict]:
        order_types = self._get(
            endpoint="public/ordertypes",
            auth=False,
        )
        return order_types

    def get_symbol_order_types(self, symbol: str) -> List[str]:
        order_types = self._get(
            endpoint=f"public/{symbol}/ordertypes",
            auth=False,
        )
        return order_types

    def get_all_market_summaries(self) -> List[dict]:
        market_summaries = self._get(
            endpoint="public/marketsummary",
            auth=False,
        )
        return market_summaries

    def get_symbol_market_summary(self, symbol: str) -> dict:
        market_summary = self._get(
            endpoint=f"public/{symbol}/marketsummary",
            auth=False,
        )
        return market_summary

    def get_trade_history(
        self,
        symbol: str,
        skip: int = 0,
        limit: int = 10,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> List[dict]:
        params = {
            "skip": skip,
            "limit": limit,
            "startTime": start_time,
            "endTime": end_time,
        }
        trade_history = self._get(
            endpoint=f"public/{symbol}/trades",
            params=params,
            auth=False,
        )
        return trade_history

    def get_server_time(self) -> dict:
        server_time = self._get(
            endpoint="public/time",
            auth=False,
        )
        return server_time

    def get_exchange_status(self) -> dict:
        exchange_status = self._get(
            endpoint="public/status",
            auth=False,
        )
        return exchange_status

    # ========== ACCOUNT INFO ==========:

    def get_current_api_key_info(self) -> dict:
        info = self._get(
            endpoint="account/api-keys/current",
            auth=True,
        )
        return info

    def get_subaccounts(self) -> List[dict]:
        subaccounts = self._get(
            endpoint="account/subaccounts",
            auth=True,
        )
        return subaccounts

    def get_non_zero_balances(self) -> List[dict]:
        balances = self._get(
            endpoint="account/balances/all",
            auth=True,
        )
        return balances

    def register_subaccount(self, label: str) -> dict:
        params = {
            "label": label,
        }
        response = self._post(
            endpoint="account/subaccount",
            params=params,
            auth=True,
        )
        return response

    def make_internal_transfer(
        self,
        from_id: str,
        to_id: str,
        symbol: str,
        amount: float,
    ) -> dict:
        params = {
            "fromId": from_id,
            "toId": to_id,
            "currencyCode": symbol,
            "amount": amount,
        }
        response = self._post(
            endpoint="account/subaccounts/transfer",
            params=params,
            auth=True,
        )
        return response

    def get_balances(self) -> List[dict]:
        balances = self._get(
            endpoint="account/balances",
            auth=True,
        )
        return balances

    def get_transaction_history(
        self,
        skip: int = 0,
        limit: int = 200,
        currency: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        transaction_types: Optional[List[TransactionType]] = None,
    ) -> List[dict]:
        params = {
            "skip": skip,
            "limit": limit,
            "currency": currency,
            "startTime": start_time,
            "endTime": end_time,
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

    def get_symbol_trade_history(self, symbol: str, limit: int = 10) -> List[dict]:
        params = {
            "limit": limit,
        }
        trade_history = self._get(
            endpoint=f"account/{symbol}/tradehistory",
            params=params,
            auth=True,
        )
        return trade_history

    # ========== WALLET INFO ==========:

    def get_currency_deposit_address(self, currency: str) -> dict:
        deposit_address = self._get(
            endpoint=f"wallet/crypto/{currency}/deposit/address",
            auth=True,
        )
        return deposit_address

    def get_whitelisted_withdrawal_address_book(self) -> List[dict]:
        address_book = self._get(
            endpoint="wallet/crypto/address-book",
            auth=True,
        )
        return address_book

    def get_currency_whitelisted_withdrawal_address_book(self, currency: str) -> dict:
        address_book = self._get(
            endpoint=f"wallet/crypto/address-book/{currency}",
            auth=True,
        )
        return address_book

    def get_withdrawal_info(self, currency: str) -> dict:
        info = self._get(
            endpoint=f"wallet/crypto/{currency}/withdraw",
            auth=True,
        )
        return info

    def make_crypto_withdrawal(self, currency: str, amount: str, address: str) -> dict:
        params = {
            "amount": amount,
            "address": address,
        }
        response = self._post(
            endpoint=f"wallet/crypto/{currency}/withdraw",
            params=params,
            auth=True,
        )
        return response

    def get_withdrawal_status(self, currency: str, withdrawal_id: str) -> dict:
        status = self._get(
            endpoint=f"wallet/crypto/{currency}/withdraw/{withdrawal_id}",
            auth=True,
        )
        return status

    def get_deposit_history(
        self, currency: str, skip: int = 0, limit: int = 10
    ) -> dict:
        params = {
            "skip": skip,
            "limit": limit,
        }
        history = self._get(
            endpoint=f"wallet/crypto/{currency}/receive/history",
            params=params,
            auth=True,
        )
        return history

    def get_withdrawal_history(
        self, currency: str, skip: int = 0, limit: int = 10
    ) -> dict:
        params = {
            "skip": skip,
            "limit": limit,
        }
        history = self._get(
            endpoint=f"wallet/crypto/{currency}/withdraw/history",
            params=params,
            auth=True,
        )
        return history

    def get_associated_bank_accounts(self, currency: str) -> List[dict]:
        accounts = self._get(
            endpoint=f"wallet/fiat/{currency}/accounts",
            auth=True,
        )
        return accounts

    def get_deposit_reference(self, currency: str) -> dict:
        reference = self._get(
            endpoint=f"wallet/fiat/{currency}/deposit/reference",
            auth=True,
        )
        return reference

    def make_fiat_withdrawal(
        self, currency: str, amount: str, bank_account_id: str, fast: bool
    ) -> dict:
        params = {
            "amount": amount,
            "linkedBankAccountId": bank_account_id,
            "fast": fast,
        }
        response = self._get(
            endpoint=f"wallet/fiat/{currency}/withdrawal",
            params=params,
            auth=True,
        )
        return response

    def get_wire_accounts(self) -> List[dict]:
        accounts = self._get(
            endpoint="wire/accounts",
            auth=True,
        )
        return accounts

    def make_wire_withdrawal(self, amount: str, wire_account_id: str) -> dict:
        params = {
            "amount": amount,
            "wireBankAccountId": wire_account_id,
        }
        response = self._post(
            endpoint="wire/withdrawals",
            params=params,
            auth=True,
        )
        return response

    # ========== SIMPLE TRADE ENDPOINTS ==========:

    def get_simple_trade_quote(
        self, symbol: str, pay_currency: str, pay_amount: str, side: OrderSide
    ) -> dict:
        params = {
            "payInCurrency": pay_currency,
            "payAmount": pay_amount,
            "side": side,
        }
        response = self._post(
            endpoint=f"simple/{symbol}/quote",
            params=params,
            auth=True,
        )
        return response

    def submit_simple_order(
        self, symbol: str, pay_currency: str, pay_amount: str, side: OrderSide
    ) -> dict:
        params = {
            "payInCurrency": pay_currency,
            "payAmount": pay_amount,
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
        amount: str,
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
            "amount": amount,
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
        quantity: str,
        price: str,
        post_only: Optional[bool] = None,
        client_order_id: Optional[int] = None,
        time_in_force: TimeInForce = TimeInForce.GTC,
    ) -> dict:
        params = {
            "side": side,
            "quantity": quantity,
            "price": price,
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
        return response

    def place_market_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: str,
        client_order_id: Optional[int] = None,
    ) -> dict:
        params = {
            "pair": symbol,
            "side": side,
            "quantity": quantity,
            "customerOrderId": client_order_id,
        }
        response = self._post(
            endpoint="orders/market",
            params=params,
            auth=True,
        )
        return response

    def place_trigger_limit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: str,
        price: str,
        trigger_price: str,
        order_type: TriggerOrderType,
        client_order_id: Optional[int] = None,
        time_in_force: TimeInForce = TimeInForce.GTC,
    ) -> dict:
        params = {
            "pair": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "stopPrice": trigger_price,
            "type": order_type,
            "customerOrderId": client_order_id,
            "timeInForce": time_in_force,
        }
        response = self._post(
            endpoint="orders/stop/limit",
            params=params,
            auth=True,
        )
        return response

    def get_order_status(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        client_order_id: Optional[int] = None,
    ) -> dict:
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
        return status

    def get_open_orders(self) -> List[dict]:
        open_orders = self._get(
            endpoint="orders/open",
            auth=True,
        )
        return open_orders

    def get_order_history(
        self, skip: int = 0, limit: Optional[int] = None
    ) -> List[dict]:
        params = {
            "skip": skip,
            "limit": limit,
        }
        order_history = self._get(
            endpoint="orders/history",
            params=params,
            auth=True,
        )
        return order_history

    def get_old_order_summary(
        self,
        order_id: Optional[str] = None,
        client_order_id: Optional[int] = None,
    ) -> dict:
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
        return summary

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
