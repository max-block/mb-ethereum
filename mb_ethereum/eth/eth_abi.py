import string
from dataclasses import dataclass
from typing import Any, Dict, Union

import eth_abi
import eth_utils
import pydash
from eth_typing import HexStr
from pydantic import BaseModel
from web3 import Web3
from web3.auto import w3

from mb_ethereum.eth.eth_utils import hex_to_bytes


@dataclass
class NameTypeValue:
    name: str
    type: str
    value: Any


class DecodedFunctionInput(BaseModel):
    function_abi: dict
    params: Dict[str, Any]

    def decode_params_bytes(self):
        result: dict[str, Any] = {}
        for k, v in self.params.items():
            if isinstance(v, bytes):
                try:
                    str_value = eth_utils.to_text(v)
                except UnicodeDecodeError:
                    str_value = eth_utils.to_hex(v)
                result[k] = "".join(filter(lambda x: x in string.printable, str_value))
            else:
                result[k] = v
        return result

    def function_signature(self):
        inputs = [i["name"] for i in self.function_abi["inputs"]]
        return self.function_abi["name"] + f"({','.join(inputs)})"

    def to_list(self, decode_bytes=False) -> list[NameTypeValue]:
        result = []
        for param in self.function_abi["inputs"]:
            name = param["name"]
            type_ = param["type"]
            value = self.params[name]
            if decode_bytes and isinstance(value, bytes):
                try:
                    value = eth_utils.to_text(value)
                except UnicodeDecodeError:
                    value = eth_utils.to_hex(value)
            result.append(NameTypeValue(name, type_, value))
        return result


def decode_function_input(contract_abi: dict, tx_input: str) -> DecodedFunctionInput:
    contract = w3.eth.contract(abi=contract_abi)
    func, params = contract.decode_function_input(HexStr(tx_input))
    return DecodedFunctionInput(function_abi=func.abi, params=params)


def encode_function_input(abi: Union[dict, list], fn_name: str, args: list) -> str:
    if isinstance(abi, list):
        abi = pydash.find(
            abi,
            lambda x: x.get("name", None) == fn_name and x.get("type", None) == "function",
        )  # type:ignore
        if not abi:
            raise ValueError("can't find abi for function: " + fn_name)

    # need update all address values to checkSum version
    processed_args = []
    for idx, arg in enumerate(abi["inputs"]):  # type:ignore
        if arg["type"] == "address":
            processed_args.append(eth_utils.to_checksum_address(args[idx]))
        else:
            processed_args.append(args[idx])

    return Web3().eth.contract(abi=[abi]).encodeABI(fn_name=fn_name, args=processed_args)


def encode_function_signature(func_name_with_types: str):
    """input example 'transfer(address,uint256)'"""
    return eth_utils.to_hex(Web3.sha3(text=func_name_with_types))[:10]


def decode_single(type_: str, data: str):
    return eth_abi.decode_single(type_, hex_to_bytes(data))


def decode_data(types: list[str], data: str):
    return eth_abi.decode_abi(types, hex_to_bytes(data))


def encode_data(types: list[str], args: list[Any]) -> str:
    return eth_utils.to_hex(eth_abi.encode_abi(types, args))


def parse_function_signatures(abi: list[dict]) -> Dict[str, str]:
    """returns dict, key: function_name_and_types, value: 4bytes signature"""
    result: Dict[str, str] = {}
    for item in abi:
        if item.get("type", None) == "function":
            function_name = item["name"]
            types = ",".join([i["type"] for i in item["inputs"]])
            function_name_and_types = f"{function_name}({types})"
            result[function_name_and_types] = encode_function_signature(function_name_and_types)
    return result
