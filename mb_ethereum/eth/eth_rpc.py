import json
import socket
from dataclasses import dataclass
from typing import Any, Optional, Union

import websocket
from mb_commons import Result, hrequest, md
from pydantic import BaseModel


@dataclass
class EventLog:
    address: str
    block_hash: str
    block_number: int
    data: str
    log_index: int
    removed: bool
    topics: list[str]
    tx_hash: str
    tx_index: int


@dataclass
class TxReceipt:
    tx_hash: str
    tx_index: int
    block_number: int
    from_address: str
    to_address: Optional[str]
    contract_address: Optional[str]
    status: Optional[int]


class TxData(BaseModel):
    block_number: Optional[int]  # for pending tx it can be none
    from_: str
    to: Optional[str]
    gas: int
    gas_price: int
    value: int
    hash: str
    input: str
    nonce: int
    v: int
    r: str
    s: str


def rpc_call(*, node: str, method: str, params: list[Any], id_=1, timeout=10, proxy=None) -> Result:
    data = {"jsonrpc": "2.0", "method": method, "params": params, "id": id_}
    if node.startswith("http"):
        return _http_call(node, data, timeout, proxy)
    else:
        return _ws_call(node, data, timeout)


def _http_call(node: str, data: dict, timeout: int, proxy: Optional[str]) -> Result:
    res = hrequest(node, method="POST", proxy=proxy, timeout=timeout, params=data, json_params=True)
    try:
        if res.is_error():
            return res.to_error()

        err = res.json.get("error", {}).get("message", "")
        if err:
            return res.to_error(f"service_error: {err}")
        if "result" in res.json:
            return res.to_ok(res.json["result"])

        return res.to_error("unknown_response")
    except Exception as e:
        return res.to_error(f"exception: {str(e)}")


def _ws_call(node: str, data: dict, timeout: int) -> Result:
    try:
        ws = websocket.create_connection(node, timeout=timeout)
        ws.send(json.dumps(data))
        response = json.loads(ws.recv())
        ws.close()
        err = response.get("error", {}).get("message", "")
        if err:
            return Result(error=f"service_error: {err}")
        if "result" in response:
            return Result(ok=response["result"])
        return Result(error=f"unknown_response: {str(response)}")

    except socket.timeout:
        return Result("timeout")
    except Exception as err:
        return Result(error=f"exception: {str(err)}")


def eth_block_number(node: str, timeout=10, proxy=None) -> Result[int]:
    res = rpc_call(node=node, method="eth_blockNumber", params=[], timeout=timeout, proxy=proxy)
    if res.is_error():
        return res

    res.ok = int(res.ok, 16)
    return res


def net_peer_count(node: str, timeout=10, proxy=None) -> Result[int]:
    res = rpc_call(node=node, method="net_peerCount", params=[], timeout=timeout, proxy=proxy)
    if res.is_error():
        return res

    res.ok = int(res.ok, 16)
    return res


def web3_client_version(node: str, timeout=10, proxy=None) -> Result[str]:
    return rpc_call(node=node, method="web3_clientVersion", params=[], timeout=timeout, proxy=proxy)


def net_version(node: str, timeout=10, proxy=None) -> Result[str]:
    res = rpc_call(node=node, method="net_version", params=[], timeout=timeout, proxy=proxy)
    if res.is_error():
        return res

    return res


def eth_get_code(node: str, address: str, timeout=10, proxy=None) -> Result:
    return rpc_call(node=node, method="eth_getCode", params=[address, "latest"], timeout=timeout, proxy=proxy)


def eth_send_raw_transaction(node: str, raw_tx: str, timeout=10, proxy=None) -> Result:
    return rpc_call(node=node, method="eth_sendRawTransaction", params=[raw_tx], timeout=timeout, proxy=proxy)


def eth_get_balance(node: str, address: str, timeout=10, proxy=None) -> Result[int]:
    res = rpc_call(node=node, method="eth_getBalance", params=[address, "latest"], timeout=timeout, proxy=proxy)
    if res.is_error():
        return res

    res.ok = int(res.ok, 16)
    return res


def eth_get_transaction_count(node: str, address: str, timeout=10, proxy=None) -> Result[int]:
    res = rpc_call(
        node=node,
        method="eth_getTransactionCount",
        params=[address, "latest"],
        timeout=timeout,
        proxy=proxy,
    )
    if res.is_error():
        return res

    res.ok = int(res.ok, 16)
    return res


def eth_get_block_by_number(node: str, block_number: int, full_transaction=False, timeout=10, proxy=None) -> Result:
    return rpc_call(
        node=node,
        method="eth_getBlockByNumber",
        params=[hex(block_number), full_transaction],
        timeout=timeout,
        proxy=proxy,
    )


def eth_get_logs(
    node: str,
    *,
    address=None,
    topics=None,
    from_block=None,
    to_block=None,
    timeout=10,
    proxy=None,
) -> Result[list[EventLog]]:
    params = {}
    if address:
        params["address"] = address
    if from_block is not None:
        params["fromBlock"] = hex(from_block)
    else:
        params["fromBlock"] = "earliest"
    if to_block is not None:
        params["toBlock"] = hex(to_block)

    if topics:
        params["topics"] = topics

    res = rpc_call(node=node, method="eth_getLogs", params=[params], proxy=proxy, timeout=timeout)
    if res.is_error():
        return res

    result: list[EventLog] = []
    for event_log in res.ok:
        result.append(
            EventLog(
                address=event_log["address"],
                block_hash=event_log["blockHash"],
                block_number=int(event_log["blockNumber"], 16),
                data=event_log["data"],
                log_index=int(event_log["logIndex"], 16),
                removed=event_log["removed"],
                topics=event_log["topics"],
                tx_hash=event_log["transactionHash"],
                tx_index=int(event_log["transactionIndex"], 16),
            ),
        )

    res.ok = result
    return res


def eth_get_transaction_receipt(node: str, tx_hash: str, timeout=10, proxy=None) -> Result[TxReceipt]:
    res = rpc_call(node=node, method="eth_getTransactionReceipt", params=[tx_hash], timeout=timeout, proxy=proxy)
    if res.is_error():
        return res

    try:
        status = None
        if "status" in res.ok:
            status = int(res.ok["status"], 16)
        res.ok = TxReceipt(
            tx_hash=tx_hash,
            tx_index=int(res.ok["transactionIndex"], 16),
            block_number=int(res.ok["blockNumber"], 16),
            from_address=res.ok["from"],
            to_address=res.ok.get("to"),
            contract_address=res.ok.get("contractAddress"),
            status=status,
        )
        return res
    except Exception as e:
        return Result(error=f"exception: {str(e)}")


def eth_get_transaction_by_hash(node: str, tx_hash: str, timeout=10, proxy=None) -> Result[TxData]:
    res = rpc_call(node=node, method="eth_getTransactionByHash", params=[tx_hash], timeout=timeout, proxy=proxy)
    if res.is_error():
        return res
    if res.ok is None:
        return res.new_error("not found")

    try:
        res.ok = TxData(
            block_number=int(res.ok["blockNumber"], 16) if res.ok["blockNumber"] is not None else None,
            from_=res.ok["from"],
            to=res.ok.get("to"),
            gas=int(res.ok["gas"], 16),
            gas_price=int(res.ok["gasPrice"], 16),
            value=int(res.ok["value"], 16),
            nonce=int(res.ok["nonce"], 16),
            input=res.ok["input"],
            hash=tx_hash,
            v=int(res.ok["v"], 16),
            r=res.ok.get("r"),
            s=res.ok.get("s"),
        )
        return res
    except Exception as e:
        return Result(error=f"exception: {str(e)}")


def eth_call(node: str, to: str, data: str, timeout=10, proxy=None) -> Result:
    return rpc_call(node=node, method="eth_call", params=[md(to, data), "latest"], timeout=timeout, proxy=proxy)


def eth_estimate_gas(
    node: str,
    from_: str,
    to: Optional[str] = None,
    value: Optional[int] = 0,
    data: Optional[str] = None,
    timeout=10,
    proxy=None,
) -> Result[int]:
    params: dict[str, Any] = {"from": from_}
    if to:
        params["to"] = to
    if data:
        params["data"] = data
    if value:
        params["value"] = value
    res = rpc_call(node=node, method="eth_estimateGas", params=[params], timeout=timeout, proxy=proxy)
    if res.is_error():
        return res
    try:
        res.ok = int(res.ok, 16)
        return res
    except Exception as e:
        return Result(error=f"exception: {str(e)}")


def eth_gas_price(node: str, timeout=10, proxy=None) -> Result[int]:
    res = rpc_call(node=node, method="eth_gasPrice", params=[], timeout=timeout, proxy=proxy)
    if res.is_error():
        return res
    try:
        res.ok = int(res.ok, 16)
        return res
    except Exception as e:
        return Result(error=f"exception: {str(e)}")


def eth_syncing(node: str, timeout=10, proxy=None) -> Result[Union[bool, dict]]:
    res = rpc_call(node=node, method="eth_syncing", params=[], timeout=timeout, proxy=proxy)
    if res.is_error():
        return res

    if isinstance(res.ok, dict):
        result = {}
        for k, v in res.ok.items():
            if v:
                result[k] = int(v, 16)
            else:
                result[k] = v
        if result.get("currentBlock", None) and result.get("highestBlock", None):
            result["remaining"] = result["highestBlock"] - result["currentBlock"]
        res.ok = result

    return res
