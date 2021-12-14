import json
import time
from pathlib import Path
from subprocess import Popen

import pytest
from click.testing import CliRunner
from mb_std.dotenv import get_dotenv


@pytest.fixture
def ws_node():
    return get_dotenv("WS_NODE")


@pytest.fixture
def etherscan_key():
    return get_dotenv("ETHERSCAN_KEY")


@pytest.fixture
def mnemonic():
    return "question witness snow panther glance repeat village husband chalk lunar pen gift recipe desk salute horse same shield lizard disease step bicycle sunset ski"  # noqa


@pytest.fixture
def address_tether():
    return "0xdac17f958d2ee523a2206206994597c13d831ec7"


@pytest.fixture
def address_etherdelta():
    return "0x8d12a197cb00d4747a1fe03395095ce2a5cc6819"


@pytest.fixture
def address_bnb():
    return "0xB8c77482e45F1F44dE1745F52C74426C631bDD52"


@pytest.fixture
def address_crypto_kitties():
    return "0x06012c8cf97bead5deae237070f9587f8e7a266d"


@pytest.fixture
def address_0():
    return "0x89d9c37F791cC913E3c8746F8C18c26a2a228b1F"


# noinspection SpellCheckingInspection
@pytest.fixture
def private_0():
    return "0x43284edec641b01e23716547dc3d5505f9f832df587f7e963c622a1927f0acd9"


@pytest.fixture
def address_1():
    return "0x2B5115229b9462F325633552385F595e5E57f62b"


@pytest.fixture
def private_1():
    return "0x3b530e5675f08000517359a1fec606009873226606d9c76b60c656b3223b6fcf"


@pytest.fixture
def address_2():
    return "0xbC443d432cdf5490844bA2d714D5Ae90c75d99a6"


@pytest.fixture
def private_2():
    return "0x0921779abeef8b740d6d302af2a125aeef5b3406fdbcd0ed3fc4fb01d54057fb"


@pytest.fixture
def infura():
    infura = get_dotenv("INFURA_PROJECT_ID")

    def _infura(network="mainnet", ws=False):
        if ws:
            return f"wss://{network}.infura.io/ws/v3/{infura}"
        else:
            return f"https://{network}.infura.io/v3/{infura}"

    return _infura


@pytest.fixture
def data_file():
    def _data_file(file: str) -> str:
        file_path = str(Path(__file__).parent.absolute()) + f"/data/{file}"
        with open(file_path) as f:
            return f.read()

    return _data_file


@pytest.fixture
def start_ganache():
    def _start_ganache(port: int, params: str) -> Popen:
        cmd = f"ganache-cli {params} --port {port}"
        p = Popen(cmd, shell=True)
        time.sleep(5)
        return p

    return _start_ganache


@pytest.fixture
def ganache_port():
    def _ganache_port(scenario: str) -> int:
        if scenario == "account":
            return 11001
        if scenario == "deploy":
            return 11002
        if scenario == "contract-call":
            return 11003
        if scenario == "send":
            return 11004
        if scenario == "contract-tx":
            return 11005
        if scenario == "speedup":
            return 11006
        if scenario == "cancel":
            return 11007
        if scenario == "transfer-all":
            return 11008
        if scenario == "node":
            return 11009
        if scenario == "rpc":
            return 11010
        raise ValueError(f"unknown scenario: {scenario}")

    return _ganache_port


@pytest.fixture
def cli():
    from mb_ethereum.cli import cli as mb_ethereum_cli

    def _cli(module: str, *params, json_output=True, node_port=None):
        runner = CliRunner()
        args = [module, *params]
        if node_port:
            args = ["-n", f"http://localhost:{node_port}", *args]

        res = runner.invoke(mb_ethereum_cli, args)
        return json.loads(res.output) if json_output else res.output

    return _cli
