# noinspection SpellCheckingInspection
def test_deploy(mnemonic, address_0, start_ganache, ganache_port, cli):
    port = ganache_port("deploy")
    ganache = start_ganache(port, f"-m '{mnemonic}'")
    try:
        res = cli("deploy", "tests/data/conf/deploy.yml", "-b", node_port=port)
        assert res["result"] == "0xb2f7a0da8edc813b72fe2b1d8b1413c18c6c90fcfd5d2e1da674a16722391038"
    finally:
        ganache.terminate()
