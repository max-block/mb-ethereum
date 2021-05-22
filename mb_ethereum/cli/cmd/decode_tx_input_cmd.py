import click
import yaml
from pydantic import StrictStr

from mb_ethereum.cli.helpers import BaseCmdConfig, parse_config, print_json
from mb_ethereum.eth import eth_abi


class Config(BaseCmdConfig):
    abi: StrictStr
    tx_input: StrictStr


@click.command(name="decode-tx-input", help="Decode tx input")
@click.argument("config_path", type=click.Path(exists=True))
@click.pass_context
def cli(ctx, config_path):
    config = parse_config(ctx, config_path, Config)
    res = eth_abi.decode_function_input(yaml.full_load(config.abi), config.tx_input)
    print_json(res)
