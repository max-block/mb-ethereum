# noinspection SpellCheckingInspection
def test_decode_raw_tx(cli):
    raw_tx = "0xf870808502cb4178008255f0949ecf07d003c4ef6c820ab511f49822099bc823da880de0b6b3a7640000820123822d45a0967a5c5a810e0290a18d1310d3a3ff0b406ed20adc73b801308c21afae188ee0a0064593c920d3b05fa5ac6ae377ce3309628830c5a8494c15880503ae55a1fa21"  # noqa
    res = cli("decode-raw-tx", raw_tx)
    assert res == {
        "tx_hash": "0x4994709b4532879af8d0a4f4e8dc003c63e9c63fe40ff2a8d4ff81405e010996",
        "from": "0x202EF8BDBa8A6AE4eFf89F6E8F9fceD2352B8760",
        "to": "0x9ecF07d003C4Ef6C820Ab511f49822099BC823Da",
        "nonce": 0,
        "gas": 22000,
        "gas_price": 12000000000,
        "value": 1000000000000000000,
        "data": "0x0123",
        "chain_id": 5777,
        "r": "0x967a5c5a810e0290a18d1310d3a3ff0b406ed20adc73b801308c21afae188ee0",
        "s": "0x64593c920d3b05fa5ac6ae377ce3309628830c5a8494c15880503ae55a1fa21",
        "v": 11589,
        "human_readable": {"gas_price": "12.0 gwei", "value": "1.0 ether", "gas": "22_000", "chain_id": "5777"},
    }
