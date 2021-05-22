import click
from mb_commons import ParallelTasks, str_to_list
from pydantic import StrictStr, validator

from mb_ethereum.cli.helpers import BaseCmdConfig, parse_config, print_config_and_exit, print_json
from mb_ethereum.eth import eth_rpc


class Config(BaseCmdConfig):
    nodes: list[StrictStr]

    @validator("nodes", pre=True)
    def to_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return str_to_list(v, unique=True, remove_comments=True)
        return v


@click.command(name="node", help="Print RPC nodes info")
@click.argument("config_path", type=click.Path(exists=True))
@click.pass_context
def cli(ctx, config_path):
    config = parse_config(ctx, config_path, Config)
    print_config_and_exit(ctx, config)

    tasks = ParallelTasks()
    for node in config.nodes:
        tasks.add_task(node, _get_node_info, args=(node,))
    tasks.execute()

    result = {}
    for node in config.nodes:
        result[node] = tasks.result[node]

    print_json(result)


def _get_node_info(node: str):
    tasks = ParallelTasks()
    tasks.add_task("block_number", _get_block_number, args=(node,))
    tasks.add_task("syncing", _get_syncing, args=(node,))
    tasks.add_task("network", _get_network, args=(node,))
    tasks.add_task("peers", _get_peers, args=(node,))
    tasks.execute()
    return tasks.result


def _get_peers(node):
    return eth_rpc.net_peer_count(node).ok_or_error


def _get_network(node):
    return eth_rpc.net_version(node).ok_or_error


def _get_block_number(node):
    return eth_rpc.eth_block_number(node).ok_or_error


def _get_syncing(node):
    return eth_rpc.eth_syncing(node).ok_or_error
