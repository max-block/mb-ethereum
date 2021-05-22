def test_contract_call(mnemonic, address_0, start_ganache, ganache_port, cli):
    port = ganache_port("contract-call")
    ganache = start_ganache(port, f"-m '{mnemonic}'")
    try:
        cli("deploy", "tests/data/conf/deploy.yml", "-b", node_port=port)
        res = cli("contract-call", "tests/data/conf/contract-call.yml", node_port=port, json_output=False)
        assert "0x00000000000000000000000000000000000000000000d3c21bcecceda1000000" in res
    finally:
        ganache.terminate()
