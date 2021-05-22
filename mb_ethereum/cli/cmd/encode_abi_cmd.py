import click
import yaml

from mb_ethereum.eth import eth_abi


@click.command(name="encode-abi", help="Encode API for data: types and args")
@click.argument("types")
@click.argument("args")
def cli(types, args):
    types = yaml.full_load(types)
    args = yaml.full_load(args)
    click.echo(eth_abi.encode_data(types, args))
