from pathlib import Path

import click


@click.command(name="example", help="Print config or arg example for a module and exit")
@click.argument(
    "module",
    type=click.Choice(
        [
            "account",
            "cancel",
            "contract-call",
            "contract-tx",
            "convert",
            "decode-bytes",
            "decode-raw-tx",
            "node",
            "rpc",
            "send",
            "deploy",
            "sign",
            "speedup",
            "transfer-all",
        ],
    ),
)
def cli(module):
    if module == "convert":
        click.echo("mb-eth convert 1300000000000000000")
        click.echo("mb-eth convert '11.5 gwei'")
        click.echo("mb-eth convert '0.05 ether'")
    elif module == "decode-raw-tx":
        raw_tx = "0xf870808502cb4178008255f0949ecf07d003c4ef6c820ab511f49822099bc823da880de0b6b3a7640000820123822d45a0967a5c5a810e0290a18d1310d3a3ff0b406ed20adc73b801308c21afae188ee0a0064593c920d3b05fa5ac6ae377ce3309628830c5a8494c15880503ae55a1fa21"  # noqa
        click.echo(f"mb-eth decode-raw-tx {raw_tx}")
    elif module == "decode-bytes":
        cmd = 'mb-ethereum decode-bytes \'["address", "uint256"]\' 00000000000000000000000080d024577781b589744d340cbfc5e85c5b526e3f0000000000000000000000000000000000000000000000000000000006772d1d'  # noqa
        click.echo(cmd)
    else:
        example_file = Path(Path(__file__).parent.absolute(), "../examples", f"{module}.yml")
        click.echo(example_file.read_text())
