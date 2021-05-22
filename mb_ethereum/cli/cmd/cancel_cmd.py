import click
from pydantic import StrictStr, validator

from mb_ethereum.cli.helpers import BaseCmdConfig, parse_config, print_json
from mb_ethereum.eth import eth_rpc, eth_tx, eth_utils


class Config(BaseCmdConfig):
    tx_hash: StrictStr
    private_key: StrictStr
    node: StrictStr
    gas_price: int
    chain_id: int = 1

    @validator("gas_price", pre=True)
    def to_wei_validator(cls, v):
        return eth_utils.to_wei(v)


@click.command(name="cancel", help="Cancel a pending tx")
@click.argument("config_path", type=click.Path(exists=True))
@click.option("--broadcast", "-b", is_flag=True, help="Broadcast a tx")
@click.pass_context
def cli(ctx, config_path, broadcast: bool):
    config = parse_config(ctx, config_path, Config)
    res = eth_rpc.eth_get_transaction_by_hash(config.node, config.tx_hash)
    if res.is_error():
        return print_json({"error": res.error})

    tx = res.ok

    new_tx = eth_tx.sign_tx(
        nonce=tx.nonce,
        gas_price=config.gas_price,
        gas=21_000,
        private_key=config.private_key,
        chain_id=config.chain_id,
        data=None,
        value=0,
        to=tx.from_,
    )
    if broadcast:
        res = eth_rpc.eth_send_raw_transaction(config.node, new_tx.raw_tx)
        print_json({"result": res.ok_or_error})
    else:
        decoded = eth_tx.decode_raw_tx(new_tx.raw_tx)
        print_json(new_tx.dict() | {"decoded": eth_utils.to_human_readable_tx(decoded)})
