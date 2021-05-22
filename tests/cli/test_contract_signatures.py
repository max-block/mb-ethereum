def test_contract_signatures(cli):
    res = cli("contract-signatures", "tests/data/abi/etherdelta.json")
    assert "admin()" in res
