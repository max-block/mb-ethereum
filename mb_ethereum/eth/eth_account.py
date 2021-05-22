from dataclasses import dataclass
from typing import Optional

from eth_account import Account
from eth_account.hdaccount import Mnemonic
from eth_keys import KeyAPI
from eth_utils import decode_hex
from eth_utils import is_address as is_address_
from mb_commons import Result

from mb_ethereum.eth import eth_rpc

key_api = KeyAPI()

Account.enable_unaudited_hdwallet_features()


@dataclass
class GeneratedAccount:
    path: str
    address: str
    private_key: str


def is_address(address: Optional[str]) -> bool:
    return is_address_(address)


def is_valid_private_key(address: str, private_key: str) -> bool:
    # noinspection PyBroadException
    try:
        return key_api.PrivateKey(decode_hex(private_key)).public_key.to_address() == address.lower()
    except Exception:
        return False


def private_to_address(private_key: str) -> str:
    return key_api.PrivateKey(decode_hex(private_key)).public_key.to_address()


def private_to_public(private_key: str) -> str:
    return key_api.PrivateKey(decode_hex(private_key)).public_key.to_hex()


def is_contract(node: str, address: str, timeout=10, proxy=None) -> Result[bool]:
    res = eth_rpc.eth_get_code(node, address, timeout=timeout, proxy=proxy)
    if res.is_error():
        return res

    res.ok = res.ok != "0x"
    return res


def truncate_address(address: str, size=3, middle="..") -> str:
    # fmt: off
    return "0x" + address[2: 2 + size] + middle + address[-size:]
    # fmt: on


def generate_mnemonic(num_words=24) -> str:
    return Mnemonic("english").generate(num_words=num_words)


def generate_accounts(*, mnemonic: Optional[str] = None, num_words=24, limit=12) -> list[GeneratedAccount]:
    result: list[GeneratedAccount] = []
    if not mnemonic:
        mnemonic = generate_mnemonic(num_words)
    for i in range(limit):
        path = f"m/44'/60'/0'/0/{i}"
        acc = Account.from_mnemonic(mnemonic=mnemonic, account_path=path)
        result.append(GeneratedAccount(path, acc.address, acc.privateKey.hex()))
    return result
