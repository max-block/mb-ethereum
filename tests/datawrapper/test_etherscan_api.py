import pytest

from mb_eth.datawrapper import etherscan_api


@pytest.mark.web
def test_get_contract_source_code(etherscan_key, address_etherdelta):
    res = etherscan_api.get_contract_source_code(etherscan_key, address_etherdelta)
    assert res.ok.contract_name == "EtherDelta"


@pytest.mark.web
def test_get_first_activity(etherscan_key):
    res = etherscan_api.get_first_activity(etherscan_key, "0x58f56615180a8eea4c462235d9e215f72484b4a3")
    assert res.ok.day == 13

    res = etherscan_api.get_first_activity(etherscan_key, "0x58f56615180a8eea4c462235d9e215f72484b4a1")
    assert not res.is_error() and res.ok is None


@pytest.mark.web
def test_get_contract_txs(etherscan_key, address_etherdelta):
    res = etherscan_api.get_account_txs(etherscan_key, address_etherdelta, 9_000_000, 9_001_000)
    assert len(res.ok) == 180
