import json
from dataclasses import dataclass
from datetime import datetime, timezone

import pydash
from mb_commons import Result, hrequest


@dataclass
class EtherscanTx:
    block_number: int
    timestamp: int
    hash: str
    transaction_index: int
    nonce: int
    from_address: str
    to_address: str
    value: int
    gas: int
    gas_price: int
    is_error: bool
    gas_used: int
    input: str


@dataclass
class EtherscanSourceCode:
    source_code: str
    abi: list[dict]
    contract_name: str


def get_contract_source_code(api_key: str, address: str, timeout=10, proxy=None) -> Result[EtherscanSourceCode]:
    params = {"module": "contract", "action": "getsourcecode", "address": address, "apikey": api_key}
    res = hrequest("https://api.etherscan.io/api", params=params, proxy=proxy, timeout=timeout)
    try:
        if res.is_error():
            return res.to_error()
        contract_name = res.json["result"][0]["ContractName"]
        abi = res.json["result"][0]["ABI"]
        source_code = res.json["result"][0]["SourceCode"]
        if "source code not verified" in abi:
            return res.to_error("not_verified")

        elif contract_name:
            abi = json.loads(abi)
            return res.to_ok(EtherscanSourceCode(source_code=source_code, contract_name=contract_name, abi=abi))

        else:
            return res.to_error("unknown_response")
    except Exception as e:
        return res.to_error(f"exception: {str(e)}")


def get_first_activity(api_key: str, address: str, timeout=10, proxy=None) -> Result[datetime]:
    oldest_block_time, oldest_block_number = None, None
    # txlist
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "sort": "asc",
        "page": 1,
        "offset": 1,
        "apikey": api_key,
    }
    res = hrequest("https://api.etherscan.io/api", params=params, proxy=proxy, timeout=timeout)

    try:
        if res.is_error():
            return res.to_error()
        if res.json.get("status") == "1":
            oldest_block_time = datetime.fromtimestamp(int(pydash.get(res.json, "result[0].timeStamp")))
            oldest_block_number = int(pydash.get(res.json, "result[0].blockNumber"))
        elif "no transactions found" in res.json.get("message", "").lower():
            pass
        else:
            return res.to_error("unknown_response")

        # tokentx
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "sort": "asc",
            "page": 1,
            "offset": 1,
            "apikey": api_key,
        }
        if oldest_block_number:
            params["startblock"] = 0
            params["endblock"] = oldest_block_number
        res = hrequest("https://api.etherscan.io/api", params=params, proxy=proxy, timeout=timeout)
        if res.is_error():
            return res.to_error()
        if res.json.get("status") == "1":
            oldest_block_time = datetime.fromtimestamp(int(pydash.get(res.json, "result[0].timeStamp")))
        elif "no transactions found" in res.json.get("message", "").lower():
            pass
        else:
            return res.to_error("unknown_response")

        # txlistinternal don't analyze because of "Query Timeout occured. Please select a smaller result dataset"
        if oldest_block_time:
            oldest_block_time = oldest_block_time.replace(tzinfo=timezone.utc)
        return res.to_ok(oldest_block_time)
    except Exception as e:
        return res.to_error(f"exception: {str(e)}")


def get_account_txs(
    api_key: str,
    address: str,
    from_block=None,
    to_block=None,
    sort=None,
    page=None,
    offset=None,
    timeout=10,
    proxy=None,
) -> Result[list[EtherscanTx]]:
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "apikey": api_key,
    }
    if from_block is not None:
        params["startblock"] = from_block
    if to_block is not None:
        params["endblock"] = to_block
    if sort:
        params["sort"] = sort
    if page is not None:
        params["page"] = page
    if offset is not None:
        params["offset"] = offset

    res = hrequest("https://api.etherscan.io/api", params=params, proxy=proxy, timeout=timeout)
    if res.is_error():
        return res.to_error()
    try:
        if res.json.get("message") == "OK":
            result = []
            for tx in res.json["result"]:
                result.append(
                    EtherscanTx(
                        block_number=int(tx["blockNumber"]),
                        timestamp=int(tx["timeStamp"]),
                        hash=tx["hash"],
                        transaction_index=int(tx["transactionIndex"]),
                        nonce=int(tx["nonce"]),
                        from_address=tx["from"],
                        to_address=tx["to"],
                        value=int(tx["value"]),
                        gas=int(tx["gas"]),
                        gas_price=int(tx["gasPrice"]),
                        is_error=tx["isError"] == "1",
                        gas_used=int(tx["gasUsed"]),
                        input=tx["input"],
                    ),
                )
            return res.to_ok(result)
        else:
            return res.to_error("unknown_response")
    except Exception as e:
        return res.to_error(f"exception: {str(e)}")
