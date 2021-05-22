from typing import Optional

import click
import yaml
from pydantic import StrictStr, validator

from mb_ethereum.cli.helpers import (
    BaseCmdConfig,
    file_validator,
    get_nonce_or_exit,
    parse_config,
    print_config_and_exit,
    print_json,
)
from mb_ethereum.eth import eth_abi, eth_account, eth_rpc, eth_tx, eth_utils


class Config(BaseCmdConfig):
    contract: StrictStr
    abi: StrictStr
    private_key: StrictStr
    gas: int
    gas_price: int
    value: int = 0
    nonce: Optional[int] = None
    function_name: StrictStr
    function_args: StrictStr = ""
    node: StrictStr
    chain_id: int = 1

    @validator("gas_price", pre=True)
    def validate_gas_price(cls, v):
        return eth_utils.to_wei(v)

    @validator("value", pre=False)
    def validate_value(cls, v):
        return eth_utils.to_wei(v)


@click.command(name="contract-tx", help="Send tx to a contract method")
@click.argument("config_path", type=click.Path(exists=True))
@click.option("--broadcast", "-b", is_flag=True, help="Broadcast txs")
@click.pass_context
def cli(ctx, config_path, broadcast: bool):
    config = parse_config(ctx, config_path, Config)
    config.abi = file_validator(config.abi, config_path)
    print_config_and_exit(ctx, config)

    function_args = yaml.full_load(config.function_args) if config.function_args else []
    data = eth_abi.encode_function_input(yaml.full_load(config.abi), config.function_name, function_args)
    if config.nonce is None:
        config.nonce = get_nonce_or_exit(config.node, eth_account.private_to_address(config.private_key))
    signed_tx = eth_tx.sign_tx(
        nonce=config.nonce,
        gas_price=config.gas_price,
        gas=config.gas,
        private_key=config.private_key,
        chain_id=config.chain_id,
        data=data,
        value=config.value,
        to=config.contract,
    )

    if broadcast:
        res = eth_rpc.eth_send_raw_transaction(config.node, signed_tx.raw_tx)
        if res.is_ok():
            print_json({"tx_hash": res.ok})
        else:
            print_json({"error": res.error})
    else:
        decoded = eth_utils.to_human_readable_tx(eth_tx.decode_raw_tx(signed_tx.raw_tx))
        print_json({"signed": signed_tx.dict(), "decoded": decoded})
