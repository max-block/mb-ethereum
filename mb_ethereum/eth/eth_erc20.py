import string
from dataclasses import dataclass
from typing import Optional, Tuple

from eth_abi import decode_abi, decode_single, encode_abi
from eth_typing import HexStr
from eth_utils import to_bytes, to_hex
from mb_commons import Result
from web3 import Web3

from mb_ethereum.eth import eth_abi, eth_rpc
from mb_ethereum.eth.eth_utils import hex_to_bytes

TRANSFER_METHOD = "0xa9059cbb"
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

ALLOWANCE_ABI = {
    "constant": True,
    "inputs": [{"name": "_owner", "type": "address"}, {"name": "_spender", "type": "address"}],
    "name": "allowance",
    "outputs": [{"name": "remaining", "type": "uint256"}],
    "payable": False,
    "stateMutability": "view",
    "type": "function",
}


@dataclass
class ERC20TransferEventLog:
    tx_hash: str
    block_number: int
    token_address: str
    from_address: str
    to_address: str
    value: str
    log_index: int


def get_symbol(node: str, address: str, timeout=10, proxy=None) -> Result[str]:
    res = eth_rpc.rpc_call(
        node=node,
        method="eth_call",
        params=[{"to": address, "data": "0x95d89b41"}, "latest"],
        timeout=timeout,
        proxy=proxy,
    )
    if res.is_error():
        return res
    try:
        symbol = Web3.toText(hexstr=res.ok)
        return res.new_ok("".join(filter(lambda x: x in string.printable, symbol)).strip())
    except UnicodeDecodeError as e:
        return res.new_error(str(e))


def get_decimals(node: str, address: str, timeout=10, proxy=None) -> Result[int]:
    res = eth_rpc.rpc_call(
        node=node,
        method="eth_call",
        params=[{"to": address, "data": "0x313ce567"}, "latest"],
        timeout=timeout,
        proxy=proxy,
    )
    if res.is_error():
        return res

    try:
        if res.ok == "0x":
            return res.new_error("no_decimals")

        if len(res.ok) > 66:
            result = Web3.toInt(hexstr=res.ok[0:66])
        else:
            result = Web3.toInt(hexstr=res.ok)

        return res.new_ok(result)

    except ValueError as e:
        return res.new_error(f"ValueError: {str(e)}")


def decode_transfer_input_data(input_data: str) -> Result[Tuple[str, int]]:
    input_data = input_data.lower()
    if input_data.startswith(TRANSFER_METHOD):
        # noinspection PyBroadException
        try:
            input_data = input_data.replace(TRANSFER_METHOD, "")
            return Result(ok=decode_abi(["address", "uint256"], Web3.toBytes(hexstr=input_data)))
        except Exception as err:
            return Result(error=f"exception: {str(err)}")
    return Result(error="bad_request")


def encode_transfer_input_data(recipient: str, value: int) -> str:
    input_data = hex_to_bytes(TRANSFER_METHOD) + encode_abi(["address", "uint256"], [recipient, value])
    return to_hex(input_data)


def get_erc20_transfer_event_logs(
    node: str,
    from_block: int,
    to_block: int,
    token: Optional[str] = None,
    proxy=None,
    timeout=30,
) -> Result[list[ERC20TransferEventLog]]:
    params = [
        {"topics": [TRANSFER_TOPIC], "fromBlock": hex(from_block), "toBlock": hex(to_block)},
    ]
    if token:
        params[0]["address"] = token
    res = eth_rpc.rpc_call(node=node, method="eth_getLogs", params=params, proxy=proxy, timeout=timeout)

    if res.is_error():
        return res

    try:
        result = []
        for log in res.ok:
            if len(log["topics"]) != 3:
                continue

            tx_hash = log["transactionHash"].lower()
            block_number = int(log["blockNumber"], 16)
            token_address = log["address"].lower()
            from_address = decode_single("address", to_bytes(hexstr=HexStr(log["topics"][1])))
            to_address = decode_single("address", to_bytes(hexstr=HexStr(log["topics"][2])))
            value = str(decode_single("uint", to_bytes(hexstr=HexStr(log["data"]))))
            log_index = int(log["logIndex"], 16)
            result.append(
                ERC20TransferEventLog(
                    tx_hash=tx_hash,
                    block_number=block_number,
                    token_address=token_address,
                    log_index=log_index,
                    from_address=from_address,
                    to_address=to_address,
                    value=value,
                ),
            )
        return res.new_ok(result)
    except Exception as e:
        return res.new_error(f"exception: {str(e)}")


def get_balance(node: str, token_address: str, user_address: str, timeout=10, proxy=None) -> Result[int]:
    data = "0x70a08231000000000000000000000000" + user_address[2:]
    res = eth_rpc.rpc_call(
        node=node,
        method="eth_call",
        params=[{"to": token_address, "data": data}, "latest"],
        timeout=timeout,
        proxy=proxy,
    )
    if res.is_error():
        return res

    try:
        return res.new_ok(int(res.ok, 16))
    except ValueError as e:
        return res.new_error(f"exception: {str(e)}")


def get_allowance(node: str, token_address: str, owner: str, spender: str, timeout=10, proxy=None) -> Result[int]:
    tx_data = eth_abi.encode_function_input(ALLOWANCE_ABI, "allowance", [owner, spender])
    res = eth_rpc.rpc_call(
        node=node,
        method="eth_call",
        params=[{"to": token_address, "data": tx_data}, "latest"],
        timeout=timeout,
        proxy=proxy,
    )
    if res.is_error():
        return res
    try:
        return res.new_ok(int(res.ok, 16))
    except ValueError as e:
        return res.new_error(f"exception: {str(e)}")
