import click

from mb_ethereum.cli.helpers import print_json
from mb_ethereum.eth import eth_utils


@click.command(name="convert", help="Convert value between wei, gwei, ether")
@click.argument("value")
def cli(value: str):
    if value.isdigit():
        result = int(value)
    else:
        try:
            result = eth_utils.to_wei(value)
        except ValueError:
            return print_json({"error": f"unknown value: {value}"})

    print_json({"wei": result, "gwei": result / 10 ** 9, "ether": result / 10 ** 18})
