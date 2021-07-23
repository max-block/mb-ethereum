import random
from typing import Any, Optional, cast

import click
import pydash
from mb_commons import str_to_list
from pydantic import BaseModel, Field, StrictStr, validator

from mb_ethereum.cli.helpers import (
    BaseCmdConfig,
    fatal,
    get_nonce_or_exit,
    parse_config,
    print_config_and_exit,
    print_json,
)
from mb_ethereum.eth import eth_account, eth_erc20, eth_rpc, eth_tx, eth_utils
from mb_ethereum.eth.eth_tx import SignedTx
from mb_ethereum.eth.eth_utils import to_wei


class Config(BaseCmdConfig):
    class Account(BaseModel):
        class Tx(BaseModel):
            class ERC20Transfer(BaseModel):
                recipient: StrictStr
                value: str

            to: Optional[StrictStr] = None
            nonce: Optional[int] = None
            gas: Optional[int]
            gas_price: Optional[int] = None
            data: Optional[StrictStr] = None
            value: Optional[int] = None
            erc20_transfer: Optional[ERC20Transfer] = None

            @validator("value", "gas_price", pre=True)
            def to_wei_validator(cls, v):
                return to_wei(v)

        from_: StrictStr = Field(..., alias="from")
        txs: list[Tx]

    accounts: list[Account]
    private_keys: list[StrictStr]
    gas_price: Optional[int] = None
    gas: Optional[int] = None
    value: Optional[int] = None
    nodes: list[StrictStr]
    chain_id: int = 1

    @validator("nodes", "private_keys", pre=True)
    def list_validator(cls, v):
        if isinstance(v, str):
            return str_to_list(v, unique=True)
        return v

    @validator("gas_price", "value", pre=True)
    def validate_gas_price(cls, v):
        return to_wei(v)

    @property
    def random_node(self) -> str:
        return random.choice(self.nodes)


@click.command(name="send", help="Send txs")
@click.argument("config_path", type=click.Path(exists=True))
@click.option("--broadcast", "-b", is_flag=True, help="Broadcast txs")
@click.pass_context
def cli(ctx, config_path, broadcast: bool):
    config = parse_config(ctx, config_path, Config)
    print_config_and_exit(ctx, config)

    txs = sign_txs(config)
    result: list[Any] = []
    if broadcast:
        for tx in txs:
            res = eth_rpc.eth_send_raw_transaction(config.random_node, tx.raw_tx)
            result.append([tx.tx_hash, "ok" if res.is_ok() else res.error])
    else:
        for tx in txs:
            res = eth_tx.decode_raw_tx(tx.raw_tx)
            result.append({"raw": tx.raw_tx, "tx": eth_utils.to_human_readable_tx(res)})

    print_json(result)


_last_account_nonce: dict[str, int] = {}


def _get_nonce(config: Config, acc: Config.Account, tx: Config.Account.Tx) -> int:
    nonce = tx.nonce
    if nonce is None:
        if acc.from_ in _last_account_nonce:
            nonce = _last_account_nonce[acc.from_] + 1
        else:
            nonce = get_nonce_or_exit(config.random_node, acc.from_)
    _last_account_nonce[acc.from_] = nonce
    return nonce


def _get_gas_price(config: Config, tx: Config.Account.Tx) -> int:
    gas_price = tx.gas_price if tx.gas_price else config.gas_price
    if not gas_price:
        return fatal("Use global gas_price or for each tx")
    return gas_price


def _get_private_key(config: Config, acc: Config.Account) -> str:
    private_keys: dict[str, str] = {}  # address -> private_key
    for private_key in config.private_keys:
        private_keys[eth_account.private_to_address(private_key).lower()] = private_key.lower()
    private_key = private_keys.get(acc.from_.lower())
    if not private_key:
        return fatal("There is no private_key for " + acc.from_)
    return private_key


class TokenInfo(BaseModel):
    address: str
    decimal: int
    symbol: str


_token_infos: list[TokenInfo] = []


def _get_data(config: Config, tx: Config.Account.Tx) -> Optional[str]:
    if tx.erc20_transfer:
        if not eth_account.is_address(tx.to):
            return fatal("tx.to must be a valid address for a erc20_transfer tx")
        if not eth_account.is_address(tx.erc20_transfer.recipient):
            return fatal(f"{tx.erc20_transfer.recipient} is not valid address")
        if tx.data is not None:
            return fatal("tx.data must be null for a erc_transfer tx")

        if tx.erc20_transfer.value.isdigit():
            value = int(tx.erc20_transfer.value)
        else:
            token_address = cast(str, tx.to)
            token_address = token_address.lower()
            token_info = pydash.find(_token_infos, lambda t: t.address == token_address)
            if not token_info:
                res = eth_erc20.get_symbol(config.random_node, token_address)
                if res.is_error():
                    return fatal(f"can't get symbol for token {token_address}: {res.error}")
                symbol = res.ok
                res = eth_erc20.get_decimals(config.random_node, token_address)
                if res.is_error():
                    return fatal(f"can't get decimals for token {tx.to}: {res.error}")
                decimals = res.ok
                token_info = TokenInfo(symbol=symbol, decimal=decimals, address=token_address)
                _token_infos.append(token_info)

            try:
                value = eth_utils.to_wei_token(tx.erc20_transfer.value, token_info.symbol, token_info.decimal)
            except ValueError as e:
                return fatal(
                    f"can't parse token value: '{tx.erc20_transfer.value}', symbol: {token_info.symbol}, decimals: {token_info.decimal}, error: {str(e)}"  # noqa
                )

        return eth_erc20.encode_transfer_input_data(tx.erc20_transfer.recipient, value)
    return tx.data


def sign_txs(config: Config) -> list[SignedTx]:
    result = []

    for acc in config.accounts:
        for tx in acc.txs:
            nonce = _get_nonce(config, acc, tx)
            private_key = _get_private_key(config, acc)
            data = _get_data(config, tx)
            value = tx.value if tx.value is not None else config.value
            gas = (tx.gas if tx.gas is not None else config.gas) or 21_000
            gas_price = tx.gas_price if tx.gas_price else config.gas_price
            if not gas_price:
                return fatal("Set global gas_price or tx.gas_price")

            raw_tx = eth_tx.sign_tx(
                private_key=private_key,
                nonce=nonce,
                to=tx.to,
                data=data,
                value=value,
                gas_price=gas_price,
                gas=gas,
                chain_id=config.chain_id,
            )
            result.append(raw_tx)
    return result
