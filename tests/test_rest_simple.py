import os

from dotenv import load_dotenv

from valrpy.enums import OrderType, ExchangeStatus
from valrpy.rest_connector import ValrRestConnector
from valrpy.messages import *


load_dotenv("../.env.local")


connector = ValrRestConnector(
    api_key=os.getenv("VALR_API_KEY"),
    api_secret=os.getenv("VALR_API_SECRET"),
)

SYMBOL = "BTCZAR"
CURRENCY = "BTC"
FIAT = "ZAR"


def _assert_listed_type(obj: list, desired_type: type) -> None:
    assert isinstance(obj, list)
    for item in obj:
        assert isinstance(item, desired_type)


def test_get_aggregated_orderbook() -> None:
    orderbook = connector.get_aggregated_orderbook(symbol=SYMBOL)
    assert isinstance(orderbook, AggregatedOrderbookData)


def test_get_full_orderbook() -> None:
    orderbook = connector.get_full_orderbook(symbol=SYMBOL)
    assert isinstance(orderbook, FullOrderbookData)


def test_get_currencies() -> None:
    currencies = connector.get_currencies()
    _assert_listed_type(obj=currencies, desired_type=CurrencyInfo)


def test_get_currency_pairs() -> None:
    currency_pairs = connector.get_currency_pairs()
    _assert_listed_type(obj=currency_pairs, desired_type=CurrencyPairInfo)


def test_get_all_order_types() -> None:
    all_order_types = connector.get_all_order_types()
    _assert_listed_type(obj=all_order_types, desired_type=PairOrderTypes)


def test_get_symbol_order_types() -> None:
    symbol_order_types = connector.get_symbol_order_types(symbol=SYMBOL)
    _assert_listed_type(obj=symbol_order_types, desired_type=OrderType)


def test_get_all_market_summaries() -> None:
    market_summaries = connector.get_all_market_summaries()
    _assert_listed_type(obj=market_summaries, desired_type=MarketSummaryData)


def test_get_symbol_market_summary() -> None:
    market_summary = connector.get_symbol_market_summary(symbol=SYMBOL)
    assert isinstance(market_summary, MarketSummaryData)


# underscore this test because the endpoint doesn't seem to work, for now at least
def _test_get_trade_history() -> None:
    trade_history = connector.get_trade_history(symbol=SYMBOL)
    _assert_listed_type(obj=trade_history, desired_type=HistoricalMarketTrade)


def test_get_server_time() -> None:
    server_time = connector.get_server_time()
    assert isinstance(server_time, ServerTime)


def test_get_exchange_status() -> None:
    exchange_status = connector.get_exchange_status()
    assert isinstance(exchange_status, ExchangeStatus)


def test_get_current_api_key_info() -> None:
    api_key_info = connector.get_current_api_key_info()
    assert isinstance(api_key_info, ApiKeyInfo)


def test_get_subaccounts() -> None:
    subaccounts = connector.get_subaccounts()
    _assert_listed_type(obj=subaccounts, desired_type=SubaccountInfo)


def test_get_non_zero_balances() -> None:
    balances = connector.get_non_zero_balances()
    _assert_listed_type(obj=balances, desired_type=SubaccountBalance)


def test_get_wallet_balances() -> None:
    wallet_balances = connector.get_wallet_balances()
    _assert_listed_type(obj=wallet_balances, desired_type=WalletBalance)


# underscore this test because the endpoint doesn't seem to work, for now at least
def _test_get_transaction_history() -> None:
    history = connector.get_transaction_history()
    _assert_listed_type(obj=history, desired_type=dict)


# underscore this test because the endpoint doesn't seem to work, for now at least
def _test_get_symbol_trade_history() -> None:
    trade_history = connector.get_symbol_trade_history(symbol=SYMBOL)
    _assert_listed_type(obj=trade_history, desired_type=HistoricalAccountTrade)


def test_get_currency_deposit_address() -> None:
    address = connector.get_currency_deposit_address(currency=CURRENCY)
    assert isinstance(address, str)


def test_get_whitelisted_withdrawal_address_book() -> None:
    address_book = connector.get_whitelisted_withdrawal_address_book()
    _assert_listed_type(obj=address_book, desired_type=WhitelistedAddress)


def test_get_currency_withdrawal_info() -> None:
    info = connector.get_currency_withdrawal_info(currency=CURRENCY)
    assert isinstance(info, CurrencyWithdrawalInfo)


# underscore this test because the endpoint doesn't seem to work, for now at least
def _test_get_deposit_history() -> None:
    deposit_history = connector.get_deposit_history(currency=CURRENCY)
    _assert_listed_type(obj=deposit_history, desired_type=HistoricalDeposit)


# underscore this test because the endpoint doesn't seem to work, for now at least
def _test_get_withdrawal_history() -> None:
    withdrawal_history = connector.get_withdrawal_history(currency=CURRENCY)
    _assert_listed_type(obj=withdrawal_history, desired_type=HistoricalWithdrawal)


def test_get_associated_bank_accounts() -> None:
    bank_accounts = connector.get_associated_bank_accounts(currency=FIAT)
    _assert_listed_type(obj=bank_accounts, desired_type=BankAccountDetail)


def test_get_deposit_reference() -> None:
    reference = connector.get_deposit_reference(currency=FIAT)
    assert isinstance(reference, str)


# underscore this test out because wire accounts are currently unavailable
def _test_get_wire_accounts() -> None:
    wire_accounts = connector.get_wire_accounts()
    _assert_listed_type(obj=wire_accounts, desired_type=dict)
