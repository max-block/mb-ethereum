import json
import os
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from json import JSONEncoder
from pathlib import Path
from typing import Callable, TypeVar, Union

import click
import pydash
import toml
import yaml
from click import Context
from jinja2 import Environment, Template, TemplateSyntaxError, meta
from mb_commons import shell, str_to_list
from pydantic import BaseModel, ValidationError, validator

from mb_ethereum.eth import eth_rpc


class BaseCmdConfig(BaseModel):
    @validator("*", pre=True)
    def env_template_validator(cls, v):
        return env_validator(v)

    class Config:
        extra = "forbid"


_jinja_env = Environment(autoescape=True)


def insert_jinja_env(v: str) -> str:
    try:
        ast = _jinja_env.parse(v)
        envs = meta.find_undeclared_variables(ast)
        if envs:
            data = {}
            for env in envs:
                if not os.getenv(env):
                    click.secho(f"can't get environment variable {env}", err=True, fg="red")
                    exit(1)
                data[env] = os.getenv(env)
            template = Template(v)
            return template.render(data)
        return v
    except TemplateSyntaxError as err:
        click.secho(f"jinja syntax error: {str(err)}", err=True, fg="red")
        click.secho(v)
        exit(1)


def env_validator(v):
    if isinstance(v, str):
        return insert_jinja_env(v)

    if isinstance(v, list) and len(v) and isinstance(v[0], str):
        return [insert_jinja_env(x) for x in v]

    return v


def shell_command(command: str):
    click.echo(command)
    res = shell.run_command(command)
    click.echo(res)


ConfigImpl = TypeVar("ConfigImpl")  # the variable return type


def parse_config(ctx: Context, config_path: str, config_cls: Callable[..., ConfigImpl]) -> ConfigImpl:
    file_data = read_config_file_or_exit(config_path)
    try:
        if ctx.obj["nodes"]:
            if "nodes" in file_data:
                file_data["nodes"] = ctx.obj["nodes"]
            elif "node" in file_data:
                file_data["node"] = ctx.obj["nodes"][0]
        return config_cls(**file_data)

    except ValidationError as err:
        click.secho(str(err), err=True, fg="red")
        exit(1)


def parse_nodes(value: Union[list[str], str]) -> list[str]:
    if isinstance(value, list):
        return pydash.union(value)
    elif isinstance(value, str):
        return str_to_list(value, unique=True)
    else:
        raise ValueError(f"wrong nodes type: {type(value)}")


def read_config_file_or_exit(file_path: str) -> dict:
    try:
        with open(file_path) as f:
            if file_path.endswith(".toml"):
                return toml.load(f)  # type:ignore
            return yaml.full_load(f)
    except Exception as err:
        click.secho(f"can't parse config file: {str(err)}", fg="red")
        exit(1)


def dict_to_yaml_str(data: dict) -> str:
    return yaml.dump(data)


def get_env_or_exit(key: str) -> str:
    value = os.getenv(key, None)
    if not value:
        click.secho(f"can't get environment variable {key}", err=True, fg="red")
        exit(1)
    return value


def print_config_and_exit(ctx: Context, config):
    if ctx.obj["config"]:
        print_json(config.dict())
        exit(0)


def file_validator(v: str, config_path: str):
    if len(v) > 100:
        return v
    file = Path(v)
    if file.exists():
        return file.read_text()
    else:
        config_file = Path(config_path)
        file = config_file.parent.joinpath(v)
        if file.exists():
            return file.read_text()
    return v


def fatal(message: str):
    click.secho(message, err=True, fg="red")
    exit(1)


def get_nonce_or_exit(node_: str, address: str) -> int:
    res = eth_rpc.eth_get_transaction_count(node_, address)
    if res.is_error():
        click.echo(f"can't get nonce: {res.error}")
        exit(1)

    return res.ok


class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, BaseModel):
            return o.dict()
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if is_dataclass(o):
            return asdict(o)
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, Exception):
            return str(o)
        return JSONEncoder.default(self, o)


def print_json(obj: Union[dict, list, BaseModel]):
    click.echo(json.dumps(obj, indent=2, cls=CustomJSONEncoder))
