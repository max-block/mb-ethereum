import json

from mb_eth.eth.eth_abi import (
    decode_function_input,
    decode_single,
    encode_function_input,
    encode_function_signature,
    parse_function_signatures,
)


def test_decode_function_input(data_file):
    tx_input = "0x278b8c0e0000000000000000000000001bc0bd5f8bec6cedaaf817d64ec0a84acbbb09aa000000000000000000000000000000000000000000069e10de76676d08000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007e1f0fd986c00000000000000000000000000000000000000000000000000000000000000a39da50000000000000000000000000000000000000000000000000000000032b91ffe000000000000000000000000000000000000000000000000000000000000001c80374e502ae2a05868ed8960b05f1e7c1c3df29eb30b5481048ceb4fb17c8cbb1ff3179219e4d30d25bd0d4f776713e04731f23dba91e67068ce33eb41b0d166"  # noqa
    abi = json.loads(data_file("abi/etherdelta.json"))
    res = decode_function_input(abi, tx_input)
    assert res.params["nonce"] == 850993150

    abi = json.loads(data_file("abi/cat.json"))
    tx_input = "0x45cf22304554482d410000000000000000000000000000000000000000000000000000000000000000000000000000004a3c3abf728b4401b1f4166352d7f08cfd287545"  # noqa
    res = decode_function_input(abi, tx_input)

    assert res.decode_params_bytes()["ilk"] == "ETH-A"


def test_encode_function_input(data_file):
    args = [
        "0x1BC0bd5f8BEC6cEdaaF817D64eC0a84ACBbb09aa",
        8000000000000000000000000,
        "0x0000000000000000000000000000000000000000",
        568000000000000000,
        10722725,
        850993150,
        28,
        b"\x807NP*\xe2\xa0Xh\xed\x89`\xb0_\x1e|\x1c=\xf2\x9e\xb3\x0bT\x81\x04\x8c\xebO\xb1|\x8c\xbb",
        b"\x1f\xf3\x17\x92\x19\xe4\xd3\r%\xbd\rOwg\x13\xe0G1\xf2=\xba\x91\xe6ph\xce3\xebA\xb0\xd1f",
    ]
    tx_input = "0x278b8c0e0000000000000000000000001bc0bd5f8bec6cedaaf817d64ec0a84acbbb09aa000000000000000000000000000000000000000000069e10de76676d08000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007e1f0fd986c00000000000000000000000000000000000000000000000000000000000000a39da50000000000000000000000000000000000000000000000000000000032b91ffe000000000000000000000000000000000000000000000000000000000000001c80374e502ae2a05868ed8960b05f1e7c1c3df29eb30b5481048ceb4fb17c8cbb1ff3179219e4d30d25bd0d4f776713e04731f23dba91e67068ce33eb41b0d166"  # noqa
    abi = json.loads(data_file("abi/etherdelta.json"))
    assert encode_function_input(abi, "cancelOrder", args) == tx_input


def test_decode_single():
    res = decode_single("address", "0x00000000000000000000000055d5c232d921b9eaa6b37b5845e439acd04b4dba")
    assert res == "0x55d5c232d921b9eaa6b37b5845e439acd04b4dba"


def test_encode_function_signature():
    assert encode_function_signature("transfer(address,uint265)") == "0x98b55909"


def test_parse_function_signatures(data_file):
    abi = json.loads(data_file("abi/etherdelta.json"))
    res = parse_function_signatures(abi)
    assert res["orderFills(address,bytes32)"] == "0x19774d43"
