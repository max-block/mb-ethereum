import click
import yaml
from pydantic import StrictStr

from mb_ethereum.cli.helpers import BaseCmdConfig, file_validator, parse_config, print_config_and_exit
from mb_ethereum.eth import eth_abi, eth_rpc


class Config(BaseCmdConfig):
    address: StrictStr
    abi: StrictStr
    function_name: StrictStr
    function_args: StrictStr = ""
    node: StrictStr


@click.command(name="contract-call", help="Do eth_call to a contract")
@click.argument("config_path", type=click.Path(exists=True))
@click.option("--print-data/--no-print-data", default=False)
@click.pass_context
def cli(ctx, config_path, print_data):
    config = parse_config(ctx, config_path, Config)
    config.abi = file_validator(config.abi, config_path)
    print_config_and_exit(ctx, config)

    function_args = yaml.full_load(config.function_args) if config.function_args else []
    data = eth_abi.encode_function_input(yaml.full_load(config.abi), config.function_name, function_args)
    if print_data:
        click.echo(data)
        exit(0)

    res = eth_rpc.eth_call(config.node, config.address, data)
    if res.is_ok():
        click.echo(res.ok)
    else:
        click.echo(f"error: {res.error}")
