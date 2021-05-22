def test_transfer_all(mnemonic, start_ganache, ganache_port, cli):
    port = ganache_port("transfer-all")
    ganache = start_ganache(port, f"-m '{mnemonic}'")
    try:
        res = cli("transfer-all", "tests/data/conf/transfer-all.yml", "-b", node_port=port)
        assert res["result"][2] == "0xae70d1fd5ceab8771831c33f8e75a9cfc0abf0339c5b99c8ca552ce5d89ace7e"
    finally:
        ganache.terminate()
