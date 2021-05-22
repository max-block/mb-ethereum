from typing import Optional

import click
from pydantic import Field, StrictStr, validator

from mb_ethereum.cli.helpers import BaseCmdConfig, parse_config, print_config_and_exit, print_json
from mb_ethereum.eth import eth_account, eth_tx, eth_utils


class Config(BaseCmdConfig):
    from_: StrictStr = Field(..., alias="from")
    private_key: StrictStr
    to: Optional[StrictStr]
    gas_price: int = 21000
    gas: int
    nonce: int
    data: Optional[StrictStr] = None
    value: Optional[int] = None
    chain_id: int = 1

    @validator("gas_price", "value", pre=True)
    def to_wei_validator(cls, v):
        return eth_utils.to_wei(v)


@click.command(name="sign", help="Sign a tx")
@click.argument("config_path", type=click.Path(exists=True))
@click.pass_context
def cli(ctx, config_path):
    config = parse_config(ctx, config_path, Config)
    print_config_and_exit(ctx, config)

    if not eth_account.is_valid_private_key(config.from_, config.private_key):
        print_json({"error": "wrong private key"})
        exit(1)

    raw_tx = eth_tx.sign_tx(**config.dict(exclude={"from_"}))
    print_json(raw_tx.dict() | {"decoded": eth_utils.to_human_readable_tx(eth_tx.decode_raw_tx(raw_tx.raw_tx))})
