from valrpy.utils import request_signature


def test_request_signature_1() -> None:
    signature = (
        "9d52c181ed69460b49307b7891f04658e938b21181173844b5018b2fe783a6d4c"
        "62b8e67a03de4d099e7437ebfabe12c56233b73c6a0cc0f7ae87e05f6289928"
    )
    assert signature == request_signature(
        api_secret="4961b74efac86b25cce8fbe4c9811c4c7a787b7a5996660afcc2e287ad864363",
        method="GET",
        path="/v1/account/balances",
        body="",
        timestamp=1558014486185,
        subaccount_id=None,
    )


def test_request_signature_2() -> None:
    signature = (
        "c34624540dae2c84a22adeea129424762b007b4bc0bf9c1ca226ea339184115fb"
        "89aaadfbfe534103e2c248d7ba7d9a7dc0670311f0f5a97a66717a582cada6f"
    )
    assert signature == request_signature(
        api_secret="4961b74efac86b25cce8fbe4c9811c4c7a787b7a5996660afcc2e287ad864363",
        method="POST",
        path="/v1/orders/market",
        body={
            "customerOrderId": "ORDER-000001",
            "pair": "BTCZAR",
            "side": "BUY",
            "quoteAmount": "80000",
        },
        timestamp=1558017528946,
        subaccount_id=None,
    )
