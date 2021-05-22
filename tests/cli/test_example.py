def test_example(cli):
    res = cli("example", "account", json_output=False)
    assert "0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE" in res

    res = cli("example", "send", json_output=False)
    assert "0x9ecF07d003C4Ef6C820Ab511f49822099BC823Da" in res
