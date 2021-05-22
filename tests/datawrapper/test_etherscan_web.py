import pytest

from mb_ethereum.datawrapper import etherscan_web


@pytest.mark.web
def test_get_token_usd_price(address_bnb):
    res = etherscan_web.get_token_usd_price(address_bnb)
    assert res.ok > 1

    res = etherscan_web.get_token_usd_price("0x6ac07b7c4601b5ce11de8dfe6335b871c7c4dd4d")
    assert res.error == "erc721"


# @pytest.mark.web
# def test_get_top_holders():
#     res = etherscan_web.get_top_holders("0x514910771af9ca656af840dff83e8264ecf986ca")
#     assert len(res.ok) == 50
#
#     res = etherscan_web.get_top_holders("0x514910771af9ca656af840dff83e8264ecf986c1")
#     assert len(res.ok) == 0


@pytest.mark.web
def test_get_address_info():
    res = etherscan_web.get_address_info("0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be").ok

    assert res.name == "Binance"
    assert res.tags == ["binance", "exchange"]
    assert res.tokens_usd > 1_000_000
    assert res.site == "https://www.binance.com/"
    assert not res.token


@pytest.mark.web
def test_get_top_accounts():
    res = etherscan_web.get_top_accounts()
    assert len(res.ok) >= 25


@pytest.mark.web
def test_get_contract_creation_tx_hash(address_etherdelta):
    res = etherscan_web.get_contract_creation_tx_hash(address_etherdelta)
    assert res.ok == "0xc10fc67499a037b6c2f14ae0c63b659b05bd7b553378202f96e777dd4843130f"


# @pytest.mark.web
# def test_get_token_transfers_count(address_etherdelta, address_crypto_kitties):
#     res = etherscan_web.get_token_transfers_count(address_etherdelta)
#     assert res.ok > 25_000_000
#
#     res = etherscan_web.get_token_transfers_count(address_crypto_kitties)
#     assert res.ok > 5_000_000


# @pytest.mark.web
# def test_get_etherscan_token(address_tether, address_crypto_kitties):
#     res = etherscan_web.get_etherscan_token(address_tether).ok
#     assert res.erc == "erc20"
#     assert res.symbol == "USDT"
#     assert res.total_supply > 5_000_000_000
#     assert res.decimals == 6
#     assert res.transfers_count > 25_000_000
#     assert 0.9 < res.price_usd < 1.1
#     assert res.market_cap_usd > 5_000_000_000
#     assert res.site == "https://tether.to/"
#
#     res = etherscan_web.get_etherscan_token(address_crypto_kitties).ok
#     assert res.erc == "erc721"
#     assert res.symbol == "CK"
#     assert res.total_supply > 1_900_000
#     assert res.decimals is None
#     assert res.transfers_count > 5_000_000
#     assert res.price_usd is None
#     assert res.market_cap_usd is None
#     assert res.site == "https://www.cryptokitties.co/"


@pytest.mark.web
def test_get_parity_trace():
    tx_hash = "0x38d01ff4daf9f60999894f3fd95f6c7612d91a3baa3225bcfaae4694cd8d17c9"
    res = etherscan_web.get_parity_trace(tx_hash)
    assert len(res.ok.traces) == 30


# def test_get_address_info_request_throttled(mocker):
#     html = read_data_file("etherscan/get_address_info_request_throttled.html")
#     mocker.patch("m_datawrapper.etherscan_web.hrequest", return_value=HResponse(status="ok", http_code=200, body=html)) # noqa
#     res = etherscan_web.get_address_info("0x8d12a197cb00d4747a1fe03395095ce2a5cc6819")
#     assert res.error == "request_throttled"
