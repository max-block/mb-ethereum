import click
import yaml

from mb_ethereum.cli.helpers import print_json
from mb_ethereum.eth import eth_abi


@click.command(name="decode-bytes")
@click.argument("types")
@click.argument("data")
def cli(types, data):
    """Decode bytes

    TYPES is a list of types, for example: '["address", "uint256"]'\n
    DATA is a hex data
    """
    res = eth_abi.decode_data(yaml.full_load(types), data)
    print_json(res)
