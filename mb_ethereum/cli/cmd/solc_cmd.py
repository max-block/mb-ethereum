import click

from mb_ethereum.cli.helpers import shell_command


@click.command(name="solc", help="Compile a solidity file")
@click.argument("contract_file", type=click.Path(exists=True))
@click.option("--bin/--no-bin", "bin_", default=True)
@click.option("--abi/--no-abi", default=True)
@click.option("--optimize/--no-optimize", default=True)
@click.option("--output")
def cli(contract_file, bin_, abi, optimize, output):
    bin_arg = "--bin" if bin_ else ""
    abi_arg = "--abi" if abi else ""
    optimize_arg = "--optimize" if optimize else ""
    output_arg = f"-o {output}" if output else ""
    command = f"solc {bin_arg} {abi_arg} {optimize_arg} {output_arg} {contract_file}"
    shell_command(command)
