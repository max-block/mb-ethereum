from datetime import date, datetime, timedelta

import pytest

from mb_ethereum.eth import eth_block


@pytest.mark.infura
def test_search_block_number_by_time(infura):
    res = eth_block.search_block_number_by_time(infura(), datetime(2018, 5, 13, 9, 33))
    assert abs(res.ok == 5605579) < 20


@pytest.mark.infura
def test_get_block_time(infura):
    res = eth_block.get_block_time(infura(), 8972973)
    assert res.ok - datetime(2019, 11, 21, 9, 56, 10) < timedelta(seconds=1)


@pytest.mark.infura
def test_get_block_time_and_transactions(infura):
    result = eth_block.get_block_time_and_transactions(infura(), 9_000_000).ok
    assert result.block_time.date() == date(2019, 11, 25)
    assert len(result.transactions) == 95


@pytest.mark.infura
def test_get_block(infura):
    res = eth_block.get_block(infura(), 9_000_000).ok
    assert len(res.transactions) == 95
    assert res.block_time > datetime(2000, 10, 12)
