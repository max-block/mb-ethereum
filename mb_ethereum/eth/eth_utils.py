import re
from decimal import Decimal
from typing import Union

import pydash
from eth_typing import HexStr
from eth_utils import to_bytes
from mb_commons import number_with_separator
from pydantic import BaseModel
from web3 import Web3


def parse_addresses(data: str) -> list[str]:
    data = data.lower()
    result = []
    for word in data.split():
        if len(word) == 42 and re.match("0x[a-f0-9]{40}", word):
            result.append(word)
    return pydash.uniq(result)


def to_wei(value: Union[str, int, Decimal]) -> int:
    if isinstance(value, int):
        return value
    elif isinstance(value, Decimal):
        if value != value.to_integral_value():
            raise ValueError(f"value must be integral number: {value}")
        return int(value)
    elif isinstance(value, str):
        value = value.lower().replace(" ", "").strip()
        if value.endswith("gwei"):
            value = value.replace("gwei", "")
            return int(Decimal(value) * 1000000000)
        if value.endswith("ether"):
            value = value.replace("ether", "")
            return int(Decimal(value) * 1000000000000000000)
        elif value.isdigit():
            return int(value)
        else:
            raise ValueError("wrong value " + value)

    else:
        raise ValueError(f"value has a wrong type: {type(value)}")


def to_wei_token(value: Union[str, int, Decimal], symbol: str, decimals: int) -> int:
    if isinstance(value, int):
        return value
    elif isinstance(value, Decimal):
        if value != value.to_integral_value():
            raise ValueError(f"value must be integral number: {value}")
        return int(value)
    elif isinstance(value, str):
        value = value.lower().replace(" ", "").strip()
        if value.isdigit():
            return int(value)
        try:
            return int(Decimal(value.replace(symbol.lower(), "").strip()) * (10 ** decimals))
        except Exception as e:
            raise ValueError(e)
    else:
        raise ValueError(f"value has a wrong type: {type(value)}")


def to_checksum_address(address: str) -> str:
    return Web3.toChecksumAddress(address)


def hex_to_bytes(data: str) -> bytes:
    return to_bytes(hexstr=HexStr(data))


def get_chain_name(chain_id) -> str:
    chain_id = str(chain_id)
    if chain_id == "1":
        return "mainnet"
    if chain_id == "3":
        return "ropsten"
    if chain_id == "5":
        return "goerli"
    return chain_id


def to_human_readable_tx(tx: Union[dict, BaseModel]) -> dict:
    if isinstance(tx, BaseModel):
        tx = tx.dict()
    tx["human_readable"] = {}
    tx["human_readable"]["gas_price"] = str(tx["gas_price"] / 10 ** 9) + " gwei"
    tx["human_readable"]["value"] = str(tx["value"] / 10 ** 18) + " ether"
    tx["human_readable"]["gas"] = number_with_separator(tx["gas"])
    if tx.get("chain_id") is not None:
        tx["human_readable"]["chain_id"] = get_chain_name(tx["chain_id"])

    return tx


def truncate_hex_str(hex_str: str, digits=4, replace_str="...") -> str:
    if not hex_str.startswith("0x") and not hex_str.startswith("0X"):
        raise ValueError("truncate_hex_str: hex_str must start with 0x")
    if digits <= 0:
        raise ValueError("truncate_hex_str: digits must be more than zero")
    hex_str = hex_str.removeprefix("0x").removeprefix("0X")
    if digits * 2 >= len(hex_str):
        raise ValueError("truncate_hex_str: digits is too large")
    return "0x" + hex_str[:digits] + replace_str + hex_str[-1 * digits :]  # noqa
