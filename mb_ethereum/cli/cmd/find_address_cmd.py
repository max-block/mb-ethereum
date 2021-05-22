from pathlib import Path

import click
import pydash

from mb_ethereum.cli.helpers import fatal
from mb_ethereum.eth import eth_utils


@click.command(name="find-address", help="Find ethereum addresses in a path")
@click.argument("path", type=click.Path(exists=True))
def cli(path):
    path = Path(path)
    addresses: list = []
    if path.is_file():
        _parse_file(path, addresses)
    elif path.is_dir():
        _parse_dir(path, addresses)
    else:
        fatal("can't open path")

    if addresses:
        for a in pydash.uniq(addresses):
            click.echo(a)
    else:
        click.echo("nothing found")


def _parse_dir(path: Path, addresses: list[str]):
    for item in path.iterdir():
        if item.is_file():
            _parse_file(item, addresses)
        elif item.is_dir():
            _parse_dir(item, addresses)


def _parse_file(file: Path, addresses: list[str]):
    try:
        addresses.extend(eth_utils.parse_addresses(file.read_text()))
    except UnicodeDecodeError:
        pass  # it was not a text file
