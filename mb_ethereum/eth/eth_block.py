import math
from dataclasses import dataclass
from datetime import datetime, timedelta

from mb_commons import Result, md

from mb_ethereum.eth import eth_rpc


@dataclass
class TimeAndTxs:
    block_time: datetime
    transactions: list[dict]


@dataclass
class Block:
    @dataclass
    class Transaction:
        tx_hash: str
        from_address: str
        to_address: str  # empty string for contract creation
        input_data: str
        gas: int
        gas_price: int
        value: int

    block_number: int
    block_time: datetime
    transactions: list[Transaction]


def search_block_number_by_time(node: str, search_time: datetime, timeout=10, proxy=None) -> Result[int]:
    res = eth_rpc.eth_block_number(node, timeout=timeout, proxy=proxy)
    if res.is_error():
        return res

    current_block_number = res.ok
    res = eth_rpc.eth_get_block_by_number(node, current_block_number, timeout=timeout, proxy=proxy)
    if res.is_error():
        return res

    current_block = res.ok
    current_block_time = _hex_to_datetime(current_block["timestamp"])

    res = eth_rpc.eth_get_block_by_number(node, 1, timeout=timeout, proxy=proxy)
    if res.is_error():
        return res

    first_block = res.ok
    first_block_time = _hex_to_datetime(first_block["timestamp"])
    if search_time < first_block_time:
        return Result(error="bad_request: before the first block time")
    if search_time > current_block_time:
        return Result(error="bad_request: after the current block time")

    min_block = 1
    max_block = current_block_number
    middle_block_number = 0

    counter = 0

    while True:
        counter += 1
        if counter > 30:
            return Result(ok=middle_block_number, data=md(counter))

        middle_block_number = math.floor((max_block - min_block) / 2) + min_block
        res = eth_rpc.eth_get_block_by_number(node, middle_block_number, timeout=timeout, proxy=proxy)
        if res.is_error():
            return res
        middle_block = res.ok

        middle_block_time = _hex_to_datetime(middle_block["timestamp"])

        if search_time > middle_block_time:
            min_block = middle_block_number
        else:
            max_block = middle_block_number

        diff = abs(search_time - middle_block_time)

        if diff < timedelta(hours=1):
            return Result(ok=middle_block_number, data={"counter": counter})


def get_block_time(node: str, block_number: int, timeout=10, proxy=None) -> Result[datetime]:
    res = eth_rpc.eth_get_block_by_number(node, block_number, timeout=timeout, proxy=proxy)
    if res.is_error():
        return res
    if not res.ok or "timestamp" not in res.ok:
        return res.new_error("unknown_response")

    return res.new_ok(_hex_to_datetime(res.ok["timestamp"]))


def get_block_time_and_transactions(node: str, block_number: int, timeout=10, proxy=None) -> Result[TimeAndTxs]:
    res = eth_rpc.eth_get_block_by_number(node, block_number, True, timeout=timeout, proxy=proxy)
    if res.is_error():
        return res
    if not res.ok or "timestamp" not in res.ok or "transactions" not in res.ok:
        return res.new_error("unknown_response: there is no `timestamp` or `transactions` in response")
    block_time = _hex_to_datetime(res.ok["timestamp"])
    return res.new_ok(TimeAndTxs(block_time, res.ok["transactions"]))


def get_block(node: str, block_number: int, timeout=10, proxy=None) -> Result[Block]:
    res = eth_rpc.eth_get_block_by_number(node, block_number, True, timeout=timeout, proxy=proxy)
    if res.is_error():
        return res

    if not res.ok or "timestamp" not in res.ok or "transactions" not in res.ok:
        return res.new_error("unknown_response: there is no `timestamp` or `transactions` in response")
    transactions = []
    for tx in res.ok["transactions"]:
        tx_hash = tx["hash"]
        from_address = tx["from"].lower()
        to_address = tx.get("to", "")
        value = int(tx["value"], 16)
        input_data = tx["input"]
        gas = int(tx["gas"], 16)
        gas_price = int(tx["gasPrice"], 16)

        transactions.append(
            Block.Transaction(**md(tx_hash, from_address, to_address, value, input_data, gas, gas_price)),
        )
    block_time = _hex_to_datetime(res.ok["timestamp"])
    return res.new_ok(Block(block_number, block_time, transactions))


def _hex_to_datetime(value: str) -> datetime:
    return datetime.fromtimestamp(int(value, 16))
