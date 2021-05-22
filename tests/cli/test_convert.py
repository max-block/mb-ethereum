def test_convert(cli):
    res = cli("convert", "1300000000000000000")
    assert res["ether"] == 1.3

    res = cli("convert", "1.3 ether")
    assert res["wei"] == 1300000000000000000

    res = cli("convert", "21.5 gwei")
    assert res["wei"] == 21500000000
