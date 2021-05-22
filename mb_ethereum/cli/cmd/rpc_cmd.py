import json
import re
from typing import Optional

import click
import yaml
from pydantic import StrictStr, validator

from mb_ethereum.cli.helpers import BaseCmdConfig, get_env_or_exit, parse_config, print_config_and_exit, print_json
from mb_ethereum.eth import eth_rpc


class Config(BaseCmdConfig):
    method: StrictStr
    node: StrictStr
    params: Optional[list]
    id: int = 1

    @validator("params", pre=True)
    def params_validator(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            try:
                res = yaml.full_load(v)
                if not isinstance(res, list):
                    raise ValueError("it's not a list")
                return res
            except Exception as err:
                raise ValueError(f"Can't parse 'params' in config: {str(err)}")
        return v if v else []

    @validator("node")
    def node_validator(cls, v):
        m = re.match(r"^\${(.+)}$", v)
        if m:
            return get_env_or_exit(m.group(1))
        return v


@click.command(name="rpc", help="Do JSON-RPC call to a node")
@click.argument("config_path", type=click.Path(exists=True))
@click.option("--curl/--no-curl", default=False, help="Print curl request and exit")
@click.pass_context
def cli(ctx, config_path, curl):
    config = parse_config(ctx, config_path, Config)
    print_config_and_exit(ctx, config)
    if curl:
        data = {"jsonrpc": "2.0", "method": config.method, "params": config.params, "id": config.id}
        data_str = json.dumps(data)
        click.echo(f"curl -H 'Content-Type: application/json' -X POST --data '{data_str}' {config.node}")
        exit(0)

    res = eth_rpc.rpc_call(node=config.node, method=config.method, params=config.params)
    print_json(res.ok_or_error)
