def test_account(mnemonic, address_0, start_ganache, ganache_port, cli):
    port = ganache_port("account")
    ganache = start_ganache(port, f"-m '{mnemonic}'")
    try:
        cli("deploy", "tests/data/conf/deploy.yml", "-b", node_port=port)
        res = cli("account", "tests/data/conf/account.yml", "--no-spinner", node_port=port)
        assert res[address_0]["nonce"] == 1
        assert res[address_0]["mb-eth"] == 1000000.0
    finally:
        ganache.terminate()
