def test_solc(cli):
    res = cli("solc", "tests/data/sol/ERC20.sol", json_output=False)
    assert "60806040523480156200001157600080fd5b50" in res
