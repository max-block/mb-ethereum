import pytest

from mb_ethereum.eth import eth_erc20

pytestmark = pytest.mark.infura


def test_get_symbol(infura, address_bnb):
    res = eth_erc20.get_symbol(infura(), address_bnb)
    assert res.ok == "BNB"

    res = eth_erc20.get_symbol(infura(), "0x1522900b6dafac587d499a862861c0869be6e428")
    assert res.error.startswith("'utf-8' codec can't")


def test_get_decimals(infura):
    res = eth_erc20.get_decimals(infura(), "0xdac17f958d2ee523a2206206994597c13d831ec7")
    assert res.ok == 6

    res = eth_erc20.get_decimals(infura(), "0xc16b542ff490e01fcc0dc58a60e1efdc3e357ca6")
    assert res.error == "no_decimals"

    res = eth_erc20.get_decimals(infura(), "0xe9cf7887b93150d4f2da7dfc6d502b216438f244")
    assert res.ok == 18


def test_get_erc20_transfer_event_logs(infura):
    # all transfers
    res = eth_erc20.get_erc20_transfer_event_logs(infura(), 9_300_000, 9_300_005)
    assert len(res.ok) == 648

    # tether only
    res = eth_erc20.get_erc20_transfer_event_logs(
        infura(),
        9_300_000,
        9_300_005,
        "0xdac17f958d2ee523a2206206994597c13d831ec7",
    )
    assert len(res.ok) == 231


def test_get_balance(infura, address_tether):
    balance = eth_erc20.get_balance(infura(), address_tether, "0xdac17f958d2ee523a2206206994597c13d831ec7").ok
    assert balance / 10 ** 6 > 1_000


def test_parse_transfer_input_data():
    data = "0xa9059cbb000000000000000000000000255e8c2357348a5befb78731715e063e85cec73d0000000000000000000000000000000000000000000000000000000003c370a0"  # noqa
    res = eth_erc20.decode_transfer_input_data(data)
    assert res.ok == ("0x255e8c2357348a5befb78731715e063e85cec73d", 63140000)

    data = "0xa9059cbb100000000000000000000000255e8c2357348a5befb78731715e063e85cec73d0000000000000000000000000000000000000000000000000000000003c370a1"  # noqa
    res = eth_erc20.decode_transfer_input_data(data)
    assert res.error.startswith("exception:")


def test_encode_transfer_input_data():
    input_data = "0xa9059cbb000000000000000000000000ade179e40ef237dc426b8a3deac0e0c74d56c31300000000000000000000000000000000000000000000000000000000063f1f00"  # noqa
    assert eth_erc20.encode_transfer_input_data("0xaDe179e40Ef237Dc426b8a3deAc0e0C74d56c313", 104800000) == input_data
