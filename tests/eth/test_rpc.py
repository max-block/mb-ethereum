import pytest

from mb_ethereum.eth import eth_rpc

pytestmark = pytest.mark.infura


def test_eth_block_number(infura):
    res = eth_rpc.eth_block_number(infura())
    assert res.ok > 9_000_000

    res = eth_rpc.eth_block_number(infura(ws=True))
    assert res.ok > 9_000_000


def test_eth_get_code(infura, address_bnb):
    res = eth_rpc.eth_get_code(infura(), address_bnb)
    assert res.ok.startswith("0x606060405236")


def test_net_version(infura):
    res = eth_rpc.net_version(infura())
    assert res.ok == "1"


def test_eth_send_raw_transaction(infura):
    raw_tx = "0xf86c808502cb417800827148948c4213500b4a1706b905cc94d4589f169ed2971d88120a871cc00200008026a013b2c691468af8666073ed074c94a019a7cff0f3fc4f892606af9843779aae13a036a88b749196d9d2460ca297d516b726926d2f77a3a6d4f998e07e41bcb21da4"  # noqa
    res = eth_rpc.eth_send_raw_transaction(infura(), raw_tx)
    assert res.error.startswith("service_error: insufficient funds for")


def test_web3_client_version(infura):
    res = eth_rpc.web3_client_version(infura())
    assert res.ok.startswith("Geth")


def test_net_peer_count(infura):
    res = eth_rpc.net_peer_count(infura())
    assert res.ok > 1


def test_eth_get_balance(infura, address_etherdelta):
    res = eth_rpc.eth_get_balance(infura(), address_etherdelta)
    assert res.ok > 1


def test_eth_get_block_by_number(infura):
    res = eth_rpc.eth_get_block_by_number(infura(), 8972973, True)
    assert res.ok["transactions"][0]["hash"] == "0x1bc1f41a0999c4ff4afe8f17704400ba0328b8b8bf60681fb809969c2127054a"


def test_eth_get_logs(infura, address_etherdelta):
    res = eth_rpc.eth_get_logs(infura(), address=address_etherdelta, from_block=9_000_000, to_block=9_001_000)
    assert len(res.ok) == 200


def test_eth_get_transaction_receipt(infura):
    res = eth_rpc.eth_get_transaction_receipt(
        infura(),
        "0xc10fc67499a037b6c2f14ae0c63b659b05bd7b553378202f96e777dd4843130f",
    )
    assert res.ok.block_number == 3154196


def test_eth_get_transaction_by_hash(infura):
    res = eth_rpc.eth_get_transaction_by_hash(
        infura(),
        "0x11f52d6cf97fd61c261f54d38134c1dcc32d32c4d60de6e64c31e776a46e6373",
    )
    assert res.ok.block_number == 9914284


def test_eth_call(infura, address_tether):
    # get tether balance of binance_1 address
    data = "0x27e235e30000000000000000000000003f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be"
    res = eth_rpc.eth_call(infura(), to=address_tether, data=data)
    assert int(res.ok, 16) > 1_000_000


def test_eth_estimate_gas(infura, address_0, address_1):
    data = "0x27e235e30000000000000000000000003f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be"
    res = eth_rpc.eth_estimate_gas(infura(), from_=address_0, to=address_1, data=data)
    assert res.ok == 21432


def test_eth_gas_price(infura):
    res = eth_rpc.eth_gas_price(infura())
    assert res.ok > 1_000_000


def test_eth_syncing(infura):
    res = eth_rpc.eth_syncing(infura())
    assert res.ok is False
