def test_speedup(mnemonic, start_ganache, ganache_port, cli):
    port = ganache_port("speedup")
    ganache = start_ganache(port, f"-m '{mnemonic}'")
    try:
        res = cli("speedup", "tests/data/conf/speedup.yml", "-b", node_port=port)
        assert res["error"] == "not found"
    finally:
        ganache.terminate()
