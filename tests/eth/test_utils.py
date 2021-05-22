from decimal import Decimal

import pytest

from mb_ethereum.eth import eth_utils


def test_to_wei():
    assert eth_utils.to_wei(123) == 123
    assert eth_utils.to_wei(Decimal("123")) == 123

    with pytest.raises(ValueError):
        eth_utils.to_wei(Decimal("123.1"))


def test_to_checksum_address(address_0):
    assert eth_utils.to_checksum_address(address_0.lower()) == address_0


def test_truncate_hex_str(address_0, private_0):
    assert eth_utils.truncate_hex_str(address_0) == "0x89d9...8b1F"
    assert eth_utils.truncate_hex_str(private_0, digits=3, replace_str="****") == "0x432****cd9"
