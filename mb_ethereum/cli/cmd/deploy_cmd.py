from typing import Any, Optional

import click
import pydash
import yaml
from pydantic import StrictStr, validator

from mb_ethereum.cli.helpers import BaseCmdConfig, file_validator, get_nonce_or_exit, parse_config, print_json
from mb_ethereum.eth import eth_abi, eth_account, eth_rpc, eth_tx, eth_utils


class Config(BaseCmdConfig):
    private_key: StrictStr
    nonce: Optional[int] = None
    gas: int
    gas_price: int
    value: int = 0
    contract_bin: StrictStr
    constructor_types: Optional[StrictStr]
    constructor_values: Optional[StrictStr]
    chain_id: int = 1
    node: StrictStr

    @validator("gas_price", "value", pre=True)
    def to_wei_validator(cls, v):
        return eth_utils.to_wei(v)


@click.command(name="deploy", help="Deploy a contract")
@click.argument("config_path", type=click.Path(exists=True))
@click.option("--broadcast", "-b", is_flag=True, help="Broadcast tx")
@click.pass_context
def cli(ctx, config_path, broadcast: bool):
    config = parse_config(ctx, config_path, Config)
    config.contract_bin = StrictStr(file_validator(config.contract_bin, config_path))
    constructor_data = ""
    if config.constructor_types and config.constructor_values:
        constructor_types = yaml.full_load(config.constructor_types)
        constructor_values = yaml.full_load(config.constructor_values)
        constructor_data = eth_abi.encode_data(constructor_types, constructor_values)[2:]
    if ctx.obj.get("config"):
        # noinspection PyUnresolvedReferences
        print_json(config.dict() | {"constructor_data": constructor_data})
        exit(0)

    tx_params: Any = pydash.omit(config.dict(), "node", "contract_bin", "constructor_types", "constructor_values")

    tx_params["data"] = config.contract_bin + constructor_data

    if tx_params["nonce"] is None:
        tx_params["nonce"] = get_nonce_or_exit(config.node, eth_account.private_to_address(config.private_key))

    signed_tx = eth_tx.sign_tx(**tx_params)

    if broadcast:
        res = eth_rpc.eth_send_raw_transaction(config.node, signed_tx.raw_tx)
        print_json({"result": res.ok_or_error})
    else:
        decoded = eth_utils.to_human_readable_tx(eth_tx.decode_raw_tx(signed_tx.raw_tx))
        print_json(signed_tx.dict() | {"decoded": decoded})
