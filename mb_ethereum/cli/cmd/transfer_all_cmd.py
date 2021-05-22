import random

import click
import pydash
from mb_commons import md, str_to_list
from pydantic import StrictStr, validator

from mb_ethereum.cli.helpers import BaseCmdConfig, fatal, parse_config, print_json
from mb_ethereum.eth import eth_account, eth_rpc, eth_tx, eth_utils
from mb_ethereum.eth.eth_tx import SignedTx


class Config(BaseCmdConfig):
    recipient: StrictStr
    private_keys: list[StrictStr]
    nodes: list[StrictStr]
    gas_price: int
    chain_id: int = 1

    @validator("gas_price", pre=True)
    def to_wei_validator(cls, v):
        return eth_utils.to_wei(v)

    @validator("nodes", "private_keys", pre=True)
    def list_validator(cls, v):
        if isinstance(v, str):
            return str_to_list(v, unique=True)
        return v

    @validator("private_keys")
    def private_keys_validator(cls, v):
        return pydash.uniq(v)

    @property
    def random_node(self) -> str:
        return random.choice(self.nodes)


@click.command(name="transfer-all", help="Transfer all ether or tokens to one address")
@click.argument("config_path", type=click.Path(exists=True))
@click.option("--broadcast", "-b", is_flag=True, help="Broadcast tx")
@click.pass_context
def cli(ctx, config_path, broadcast: bool):
    config = parse_config(ctx, config_path, Config)

    # address -> private_key
    accounts = {eth_account.private_to_address(private_key): private_key for private_key in config.private_keys}

    tx_fee = 21_000 * config.gas_price

    low_eth_balance: list[str] = []
    signed_tx: list[SignedTx] = []

    for address, private_key in accounts.items():
        res = eth_rpc.eth_get_balance(config.random_node, address)
        if res.is_error():
            return fatal(f"can't get balance: {res.error}")
        balance = res.ok
        if balance <= tx_fee:
            low_eth_balance.append(address)
        else:
            res = eth_rpc.eth_get_transaction_count(config.random_node, address)
            if res.is_error():
                return fatal(f"can't get nonce: {res.error}")
            nonce = res.ok
            value = balance - tx_fee
            tx = eth_tx.sign_tx(
                nonce=nonce,
                gas_price=config.gas_price,
                gas=21_000,
                private_key=private_key,
                chain_id=config.chain_id,
                value=value,
                to=config.recipient,
            )
            signed_tx.append(tx)

    if broadcast:
        result = []
        for tx in signed_tx:
            res = eth_rpc.eth_send_raw_transaction(config.random_node, tx.raw_tx)
            result.append(res.ok_or_error)
        print_json(md(low_eth_balance, result))
    else:
        txs = []
        for tx in signed_tx:
            decoded = eth_tx.decode_raw_tx(tx.raw_tx)
            decoded = eth_utils.to_human_readable_tx(decoded)  # type:ignore
            txs.append(tx.dict() | md(decoded))
        print_json(md(low_eth_balance, signed_tx=txs))
