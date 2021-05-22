import random
import sys
from typing import Optional

import click
from halo import Halo
from mb_commons import ParallelTasks, str_to_list
from pydantic import StrictStr, validator

from mb_ethereum.cli.helpers import BaseCmdConfig, fatal, parse_config, print_config_and_exit, print_json
from mb_ethereum.datawrapper import etherscan_web
from mb_ethereum.eth import eth_erc20, eth_rpc

TIMEOUT = 10


class Config(BaseCmdConfig):
    addresses: list[StrictStr]
    nodes: list[StrictStr]
    proxies: Optional[list[StrictStr]] = None
    tokens: Optional[list[StrictStr]] = None
    check_nonce: bool = True
    check_eth_balance: bool = True
    check_etherscan_token_usd: bool = True

    @validator("addresses", "nodes", "tokens", "proxies", pre=True)
    def to_list_validator(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return str_to_list(v, unique=True, remove_comments=True)
        return v

    @property
    def random_node(self) -> str:
        return random.choice(self.nodes)

    @property
    def random_proxy(self) -> Optional[str]:
        return random.choice(self.proxies) if self.proxies else None


class TokenInfo(BaseCmdConfig):
    address: str
    symbol: str
    decimals: int


class AccountsChecker:
    def __init__(self, config: Config, no_spinner: bool):
        self.config = config
        self.use_spinner = not no_spinner
        self.spinner = Halo(spinner="dots", stream=sys.stderr)
        self.processed_count = 0  # processed addresses counter
        self.tokens: list[TokenInfo] = []

    def process(self) -> dict:
        self._process_tokens()

        if self.use_spinner:
            self.spinner.start()
        tasks = ParallelTasks(max_workers=3)
        for address in self.config.addresses:
            tasks.add_task(address, self._process_address, args=(address,))
        tasks.execute()
        if self.use_spinner:
            self.spinner.stop()

        result = tasks.result
        if tasks.error:
            result["errors"] = tasks.exceptions
        return result

    def _process_tokens(self):
        if self.config.tokens:
            if self.use_spinner:
                self.spinner.start()
            for idx, address in enumerate(self.config.tokens):
                self.spinner.text = f"Process token: {idx + 1} / {len(self.config.tokens)}"
                self.tokens.append(self._get_token_info(address))
            if self.use_spinner:
                self.spinner.stop()

    def _get_token_info(self, address: str) -> TokenInfo:
        res = eth_erc20.get_symbol(self.config.random_node, address, timeout=TIMEOUT)
        if res.is_error():
            return fatal(f"can't get symbol for token {address}: {res.error}")
        symbol = res.ok

        res = eth_erc20.get_decimals(self.config.random_node, address, timeout=TIMEOUT)
        if res.is_error():
            return fatal(f"can't get decimals for token {address}: {res.error}")
        decimals = res.ok

        return TokenInfo(address=address, symbol=symbol, decimals=decimals)

    def _process_address(self, address: str):
        self.spinner.text = f"Process account: {self.processed_count} / {len(self.config.addresses)}"
        tasks = ParallelTasks(timeout=TIMEOUT)
        if self.config.check_nonce:
            tasks.add_task("nonce", self._get_nonce, (address,))
        if self.config.check_eth_balance:
            tasks.add_task("ETH", self._get_eth_balance, (address,))
        if self.config.check_etherscan_token_usd:
            tasks.add_task("etherscan_tokens_usd", self._get_etherscan_tokens_usd, (address,))
        for token in self.tokens:
            tasks.add_task(token.symbol, self._get_token_balance, (address, token))
        tasks.execute()
        self.processed_count += 1
        result = tasks.result
        if tasks.error:
            result["errors"] = tasks.exceptions
        return result

    def _get_etherscan_tokens_usd(self, address: str):
        for _ in range(3):
            res = etherscan_web.get_address_info(address, timeout=5, proxy=self.config.random_proxy)
            if res.is_ok():
                return float(res.ok.tokens_usd)
        return res.error

    def _get_nonce(self, address: str):
        for _ in range(3):
            res = eth_rpc.eth_get_transaction_count(
                self.config.random_node,
                address,
                timeout=5,
                proxy=self.config.random_proxy,
            )
            if res.is_ok():
                return res.ok
        return res.error

    def _get_eth_balance(self, address: str):
        for _ in range(3):
            res = eth_rpc.eth_get_balance(
                self.config.random_node,
                address,
                timeout=TIMEOUT,
                proxy=self.config.random_proxy,
            )
            if res.is_ok():
                return res.ok / 10 ** 18
        return res.error

    def _get_token_balance(self, address: str, token: TokenInfo):
        for _ in range(3):
            res = eth_erc20.get_balance(
                self.config.random_node,
                token.address,
                address,
                timeout=TIMEOUT,
                proxy=self.config.random_proxy,
            )
            if res.is_ok():
                return res.ok / 10 ** token.decimals
        return res.error


@click.command(name="account", help="Print nonce, eth and token balances")
@click.argument("config_path", type=click.Path(exists=True))
@click.option("--no-spinner", is_flag=True, help="Don't use a spinner")
@click.pass_context
def cli(ctx, config_path, no_spinner: bool):
    config = parse_config(ctx, config_path, Config)
    print_config_and_exit(ctx, config)

    checker = AccountsChecker(config, no_spinner)
    result = checker.process()
    print_json(result)
