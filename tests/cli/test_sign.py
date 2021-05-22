def test_sign(cli):
    res = cli("sign", "tests/data/conf/sign.yml")
    assert res["tx_hash"] == "0x28429035f991af1ea5b55813da16504fa7d253cddbbfa668d629b6e019fc0004"
