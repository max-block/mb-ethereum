import json

import click

from mb_ethereum.cli.helpers import print_json
from mb_ethereum.eth import eth_abi


@click.command(name="contract-signatures", help="Print all contract signatures")
@click.argument("abi_path", type=click.Path(exists=True))
def cli(abi_path):
    with open(abi_path) as f:
        abi = json.load(f)

    res = eth_abi.parse_function_signatures(abi)
    print_json(res)
