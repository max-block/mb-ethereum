import json
from dataclasses import dataclass
from datetime import datetime
from logging import Logger
from threading import Thread
from typing import Callable, Optional
from urllib.parse import urlparse

import pydash
from cachetools import TTLCache
from mb_commons import utc_now
from websocket import WebSocketApp, enableTrace, setdefaulttimeout


@dataclass
class Tx:
    node: str
    tx_hash: str
    from_address: str
    to_address: str
    nonce: int
    gas: int
    gas_price: int
    value: int
    input_data: str
    v: int
    r: str
    s: str
    tx_hash_at: Optional[datetime]  # when tx_hash was received
    tx_at: datetime  # when tx was received

    def raw_tx(self) -> str:
        pass
        # return eth_tx.encode_raw_tx_with_signature(
        #     nonce=self.nonce,
        #     gas_price=self.gas_price,
        #     gas=self.gas,
        #     v=self.v,
        #     r=self.r,
        #     s=self.s,
        #     data=self.input_data,
        #     value=self.value,
        # )


@dataclass
class Block:
    node: str
    block_number: int
    transactions: list[str]
    created_at: datetime = utc_now()


@dataclass
class TxStats:
    tx_hash_count: int = 0  # how many tx_hashed were received
    tx_hash_last_at: Optional[datetime] = None  # how many tx_hashes were received
    tx_count: int = 0  # how many txs were received
    tx_last_at: Optional[datetime] = None  # when the last tx was received


@dataclass
class BlockStats:
    block_number_count: int = 0
    block_number_last_at: Optional[datetime] = None
    block_count: int = 0
    block_last_at: Optional[datetime] = None


class TxPoolMonitor(WebSocketApp):
    def __init__(
        self,
        log: Logger,
        ws_node: str,
        group: Optional[str] = None,
        monitor_pending_txs=False,
        monitor_blocks=False,
        on_tx_hash: Optional[Callable[[str], None]] = None,
        on_tx: Optional[Callable[[Tx], None]] = None,
        on_block_number: Optional[Callable[[int], None]] = None,
        on_block: Optional[Callable[[Block], None]] = None,
        on_error: Optional[Callable] = None,
        on_close: Optional[Callable] = None,
        timeout=10,
        debug=False,
    ):
        setdefaulttimeout(timeout)
        if debug:
            enableTrace(True)
        super().__init__(
            ws_node,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=on_error,
            on_close=on_close,
        )
        self.log = log
        self.ws_node = ws_node
        self.group = group
        self.monitor_pending_txs = monitor_pending_txs
        self.monitor_blocks = monitor_blocks
        self.on_tx_hash = on_tx_hash
        self.on_tx = on_tx
        self.on_block_number = on_block_number
        self.on_block = on_block
        self.tx_stats = TxStats()
        self.block_stats = BlockStats()
        self.created_at = utc_now()
        self.pending_txs_subscription = None
        self.jsonrpc_id = 0
        self.pending_txs_jsonrpc_id = None
        self.heads_subscription = None
        self.heads_jsonrpc_id = None
        self.tx_hash_at: TTLCache = TTLCache(ttl=10 * 60, maxsize=9_999_999)  # tx_hash -> timestamp
        self.source_count = 0

    def on_open(self):
        self.log.debug("on_open")
        self.jsonrpc_id += 1
        self.pending_txs_jsonrpc_id = self.jsonrpc_id
        if self.monitor_pending_txs:
            self.send(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "method": "eth_subscribe",
                        "params": ["newPendingTransactions"],
                        "id": self.pending_txs_jsonrpc_id,
                    },
                ),
            )

        self.jsonrpc_id += 1
        self.heads_jsonrpc_id = self.jsonrpc_id
        if self.monitor_blocks:
            self.send(
                json.dumps(
                    {"jsonrpc": "2.0", "method": "eth_subscribe", "params": ["newHeads"], "id": self.heads_jsonrpc_id},
                ),
            )

    def on_message(self, message):
        msg = json.loads(message)

        json_id = pydash.get(msg, "id")
        result = pydash.get(msg, "result")
        method = pydash.get(msg, "method")
        subscription = pydash.get(msg, "params.subscription")
        params_result = pydash.get(msg, "params.result")

        if json_id == self.pending_txs_jsonrpc_id and result:
            self.pending_txs_subscription = result
        elif json_id == self.heads_jsonrpc_id and result:
            self.heads_subscription = msg.get("result")
        elif method == "eth_subscription" and subscription == self.pending_txs_subscription and params_result:
            self._process_tx_hash(params_result)
        elif method == "eth_subscription" and subscription == self.heads_subscription and params_result:
            self._process_block_number(params_result)
        elif pydash.get(msg, "result.transactions") is not None:
            self._process_block(msg)
        elif pydash.get(msg, "result.from"):
            self._process_tx(msg)
        elif result is None and pydash.omit(msg, "jsonrpc", "result", "id") == {}:
            pass  # empty message
        else:
            pass
            # self.log.warning("unknown message: %s", message)

    def _process_block_number(self, msg: dict):
        block_number = pydash.get(msg, "number")
        if block_number:
            block_number = int(block_number, 16)
            if self.on_block_number:
                self.on_block_number(block_number)
            self.block_stats.block_number_last_at = utc_now()
            self.block_stats.block_number_count += 1
            self.jsonrpc_id += 1
            self.send(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "method": "eth_getBlockByNumber",
                        "params": [hex(block_number), False],
                        "id": self.jsonrpc_id,
                    },
                ),
            )

    def _process_tx_hash(self, tx_hash: str):
        if self.on_tx_hash:
            self.on_tx_hash(tx_hash)
        self.tx_stats.tx_hash_last_at = utc_now()
        self.tx_stats.tx_hash_count += 1
        if not self.tx_hash_at.get(tx_hash):
            self.tx_hash_at[tx_hash] = utc_now()

        self.jsonrpc_id += 1
        tx_info_request = {
            "jsonrpc": "2.0",
            "method": "eth_getTransactionByHash",
            "params": [tx_hash],
            "id": self.jsonrpc_id,
        }
        self.send(json.dumps(tx_info_request))

    def _process_tx(self, msg: dict):
        try:
            if self.on_tx:
                self.on_tx(self._parse_tx_dict(self.url, msg["result"]))
            self.tx_stats.tx_count += 1
            self.tx_stats.tx_last_at = utc_now()
        except Exception as err:
            self.log.error(err)

    def _process_block(self, msg: dict):
        block_number = pydash.get(msg, "result.number")
        transactions = pydash.get(msg, "result.transactions")
        if block_number:
            block_number = int(block_number, 16)
            if self.on_block:
                self.on_block(Block(node=self.ws_node, block_number=block_number, transactions=transactions))
            self.block_stats.block_last_at = utc_now()
            self.block_stats.block_count += 1

    def _parse_tx_dict(self, node: str, tx: dict) -> Tx:
        return Tx(
            tx_hash=tx["hash"],
            from_address=tx["from"],
            to_address=tx["to"] or "",
            nonce=int(tx["nonce"], 16),
            gas=int(tx["gas"], 16),
            gas_price=int(tx["gasPrice"], 16),
            value=int(tx["value"], 16),
            input_data=tx["input"],
            node=node,
            v=int(tx["v"], 16),
            r=tx["r"],
            s=tx["s"],
            tx_at=utc_now(),
            tx_hash_at=self.tx_hash_at.get(tx["hash"]),
        )

    def start(self):
        hostname = urlparse(self.ws_node).hostname
        Thread(target=lambda: self.run_forever(), name=f"TxPoolMonitor({hostname})").start()
