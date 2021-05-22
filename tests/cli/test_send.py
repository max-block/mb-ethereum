# noinspection SpellCheckingInspection
def test_send(mnemonic, start_ganache, ganache_port, cli):
    port = ganache_port("send")
    ganache = start_ganache(port, f"-m '{mnemonic}'")
    try:
        cli("deploy", "tests/data/conf/deploy.yml", "-b", node_port=port)
        res = cli("send", "tests/data/conf/send.yml", "-b", node_port=port)
        assert res[3][0] == "0xbe2240f99a757b777ea9efaf1d7b4cbdddc07d9b867c4de4f5f1894e4811ea11"
    finally:
        ganache.terminate()
