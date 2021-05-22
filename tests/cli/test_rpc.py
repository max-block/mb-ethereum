def test_rpc(start_ganache, ganache_port, cli):
    port = ganache_port("rpc")
    ganache = start_ganache(port, "")
    try:
        res = cli("rpc", "tests/data/conf/rpc.yml", node_port=port, json_output=False)
        assert "EthereumJS" in res
    finally:
        ganache.terminate()
