import os
from pathlib import Path
from typing import Tuple

import click
from click import Context
from dotenv import load_dotenv

from mb_ethereum import __version__
from mb_ethereum.cli.cmd import (
    account_cmd,
    cancel_cmd,
    contract_call_cmd,
    contract_signatures_cmd,
    contract_tx_cmd,
    convert_cmd,
    decode_bytes_cmd,
    decode_raw_tx_cmd,
    decode_tx_input_cmd,
    deploy_cmd,
    encode_abi_cmd,
    example_cmd,
    find_address_cmd,
    mnemonic_cmd,
    node_cmd,
    private_key_cmd,
    rpc_cmd,
    send_cmd,
    sign_cmd,
    solc_cmd,
    speedup_cmd,
    transfer_all_cmd,
)

_env_file = Path(os.getcwd()).joinpath(".env")
if _env_file.is_file():
    load_dotenv(_env_file)


@click.group()
@click.option("-c", "--config/--no-config", "config_", default=False, help="Print config and exit")
@click.option("-n", "--node", multiple=True, help="List of JSON RPC nodes, it overwrites node/nodes field in config")
@click.version_option(__version__, help="Show the version and exit")
@click.help_option(help="Show this message and exit")
@click.pass_context
def cli(ctx: Context, config_, node: Tuple[str]):
    ctx.ensure_object(dict)
    ctx.obj["config"] = config_
    ctx.obj["nodes"] = node


cli.add_command(account_cmd.cli)
cli.add_command(cancel_cmd.cli)
cli.add_command(contract_call_cmd.cli)
cli.add_command(contract_signatures_cmd.cli)
cli.add_command(contract_tx_cmd.cli)
cli.add_command(convert_cmd.cli)
cli.add_command(decode_bytes_cmd.cli)
cli.add_command(decode_raw_tx_cmd.cli)
cli.add_command(decode_tx_input_cmd.cli)
cli.add_command(deploy_cmd.cli)
cli.add_command(encode_abi_cmd.cli)
cli.add_command(example_cmd.cli)
cli.add_command(find_address_cmd.cli)
cli.add_command(mnemonic_cmd.cli)
cli.add_command(node_cmd.cli)
cli.add_command(private_key_cmd.cli)
cli.add_command(rpc_cmd.cli)
cli.add_command(send_cmd.cli)
cli.add_command(sign_cmd.cli)
cli.add_command(solc_cmd.cli)
cli.add_command(speedup_cmd.cli)
cli.add_command(transfer_all_cmd.cli)
