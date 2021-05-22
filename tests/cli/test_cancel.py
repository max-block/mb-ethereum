def test_cancel(mnemonic, start_ganache, ganache_port, cli):
    port = ganache_port("cancel")
    ganache = start_ganache(port, f"-m '{mnemonic}'")
    try:
        res = cli("cancel", "tests/data/conf/cancel.yml", "-b", node_port=port)
        assert res["error"] == "not found"
    finally:
        ganache.terminate()
