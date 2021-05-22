# noinspection SpellCheckingInspection
def test_contract_tx(mnemonic, start_ganache, ganache_port, cli):
    port = ganache_port("contract-tx")
    ganache = start_ganache(port, f"-m '{mnemonic}'")
    try:
        cli("deploy", "tests/data/conf/deploy.yml", "-b", node_port=port)
        res = cli("contract-tx", "tests/data/conf/contract-tx.yml", "-b", node_port=port)
        assert res["tx_hash"] == "0xa7c1fc4a11cf4605c511ea9bde21c247d1911e17693ef12d43ca87fce7c6b5ee"
    finally:
        ganache.terminate()
