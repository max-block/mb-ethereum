import click

from mb_ethereum.eth import eth_account


@click.command(name="private-key", help="Print address for a private key")
@click.argument("private_key")
def cli(private_key):
    try:
        click.echo(eth_account.private_to_address(private_key))
    except Exception as e:
        click.echo(f"error: {str(e)}")
