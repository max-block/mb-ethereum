def test_node(start_ganache, ganache_port, cli):
    port = ganache_port("node")
    ganache = start_ganache(port, "")
    try:
        res = cli("node", "tests/data/conf/node.yml", node_port=port)
        assert res[f"http://localhost:{port}"]["block_number"] == 0
    finally:
        ganache.terminate()
