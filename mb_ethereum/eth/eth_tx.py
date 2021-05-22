from typing import Any, Dict, Optional

import rlp
from eth_utils import keccak
from mb_commons import md
from pydantic import BaseModel
from rlp.sedes import Binary, big_endian_int, binary
from web3 import Web3
from web3.auto import w3

from mb_ethereum.eth.eth_utils import hex_to_bytes


class SignedTx(BaseModel):
    tx_hash: str
    raw_tx: str


class RPLTransaction(rlp.Serializable):
    fields = [
        ("nonce", big_endian_int),
        ("gas_price", big_endian_int),
        ("gas", big_endian_int),
        ("to", Binary.fixed_length(20, allow_empty=True)),
        ("value", big_endian_int),
        ("data", binary),
        ("v", big_endian_int),
        ("r", big_endian_int),
        ("s", big_endian_int),
    ]

    @staticmethod
    def new_tx(*, nonce, gas_price, gas, to, value, data, v, r, s):
        return RPLTransaction(nonce, gas_price, gas, to, value, data, v, r, s)


class DecodedRawTx(BaseModel):
    tx_hash: str
    from_: str
    to: Optional[str]
    nonce: int
    gas: int
    gas_price: int
    value: int
    data: str
    chain_id: int
    r: str
    s: str
    v: int


def encode_raw_tx_with_signature(
    *,
    nonce: int,
    gas_price: int,
    gas: int,
    v: int,
    r: str,
    s: str,
    data: Optional[str] = None,
    value: Optional[int] = None,
    to: Optional[str] = None,
):
    if to:
        to = hex_to_bytes(to)  # type:ignore
    if data:
        data = hex_to_bytes(data)  # type:ignore
    if not value:
        value = 0
    r = int(r, 16)  # type:ignore
    s = int(s, 16)  # type:ignore
    tx = RPLTransaction.new_tx(**md(nonce, gas_price, gas, data, value, to, v, r, s))
    return Web3.toHex(rlp.encode(tx))


def sign_tx(
    *,
    nonce: int,
    gas_price: int,
    gas: int,
    private_key: str,
    chain_id: int,
    data: Optional[str] = None,
    value: Optional[int] = None,
    to: Optional[str] = None,
) -> SignedTx:
    tx: Dict[str, Any] = {"gas": gas, "gasPrice": gas_price, "nonce": nonce, "chainId": chain_id}
    if to:
        tx["to"] = w3.toChecksumAddress(to)
    if value:
        tx["value"] = value
    if data:
        tx["data"] = data
    signed = w3.eth.account.signTransaction(tx, private_key)
    return SignedTx(tx_hash=signed.hash.hex(), raw_tx=signed.rawTransaction.hex())


def decode_raw_tx(raw_tx: str) -> DecodedRawTx:
    tx: Any = rlp.decode(hex_to_bytes(raw_tx), RPLTransaction)
    tx_hash = Web3.toHex(keccak(hex_to_bytes(raw_tx)))
    from_ = w3.eth.account.recover_transaction(raw_tx)
    to = w3.toChecksumAddress(tx.to) if tx.to else None
    data = w3.toHex(tx.data)
    r = hex(tx.r)
    s = hex(tx.s)
    chain_id = (tx.v - 35) // 2 if tx.v % 2 else (tx.v - 36) // 2
    return DecodedRawTx(**md(tx_hash, from_, to, data, chain_id, r, s, tx.v, tx.gas, tx.gas_price, tx.value, tx.nonce))
