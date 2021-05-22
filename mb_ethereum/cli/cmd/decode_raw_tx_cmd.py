import click
import pydash

from mb_ethereum.cli.helpers import print_json
from mb_ethereum.eth import eth_tx, eth_utils


@click.command(name="decode-raw-tx", help="Decode a raw tx hex")
@click.argument("raw_tx")
def cli(raw_tx):
    tx = eth_tx.decode_raw_tx(raw_tx).dict()
    tx = pydash.rename_keys(tx, {"from_": "from"})
    tx = eth_utils.to_human_readable_tx(tx)
    print_json(tx)
