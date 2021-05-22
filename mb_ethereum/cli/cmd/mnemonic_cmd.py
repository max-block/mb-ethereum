import click

from mb_ethereum.cli.helpers import print_json
from mb_ethereum.eth import eth_account


@click.command(name="mnemonic", help="Generate eth accounts based on mnemonic")
@click.option("--mnemonic", "-m")
def cli(mnemonic):
    result = {}
    if not mnemonic:
        mnemonic = eth_account.generate_mnemonic()
    result["mnemonic"] = mnemonic
    result["accounts"] = []
    for acc in eth_account.generate_accounts(mnemonic=mnemonic):
        result["accounts"].append({"public": acc.address, "private": acc.private_key})
    print_json(result)
