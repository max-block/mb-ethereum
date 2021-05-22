import pytest

from mb_ethereum.eth import eth_account


def test_is_valid_private_key(address_0, private_0):
    assert eth_account.is_valid_private_key(address_0, private_0)

    # noinspection SpellCheckingInspection
    wrong_private_key = "0x43284edec641b01e23716547dc3d5505f9f832df587f7e963c622a1927f0acd8"
    assert not eth_account.is_valid_private_key(address_0, wrong_private_key)


def test_truncate_address(address_0):
    res = eth_account.truncate_address(address_0)
    assert res == "0x89d..b1F"


def test_private_to_address(address_0, private_0):
    res = eth_account.private_to_address(private_0)
    assert res == address_0.lower()


def test_private_to_public(private_0):
    res = eth_account.private_to_public(private_0)
    public_key = "0xc8c0a52b6859738f83dac7922e9862337470e437396b57de01182f0c0240a0319f2a636f09e78afc082235c8ea65fef79e44d21d252b42374e7bad6bf499aff1"  # noqa
    assert res == public_key


def test_generate_mnemonic():
    words = eth_account.generate_mnemonic()
    assert len(words.split()) == 24


def test_generate_accounts():
    accounts = eth_account.generate_accounts(limit=11)
    assert len(accounts) == 11


@pytest.mark.infura
def test_is_contract(infura):
    res = eth_account.is_contract(infura(), "0x148709aef9e367a235da79dc21b83ce32f1f5bba")
    assert res.ok is False

    res = eth_account.is_contract(infura(), "0xd8f93d967fa21a0a826a3bd4601ada4bb468823d")
    assert res.ok is True
