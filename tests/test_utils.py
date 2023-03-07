from valrpy.utils import request_signature


def test_request_signature() -> None:
    signature = (
        "9d52c181ed69460b49307b7891f04658e938b21181173844b5018b2fe783a6d4c"
        "62b8e67a03de4d099e7437ebfabe12c56233b73c6a0cc0f7ae87e05f6289928"
    )
    assert signature == request_signature(
        api_key_secret="4961b74efac86b25cce8fbe4c9811c4c7a787b7a5996660afcc2e287ad864363",
        path="/v1/account/balances",
        method="GET",
        timestamp=1558014486185,
        body="",
    )
