import asyncio
from datetime import timedelta
from time import monotonic
import pytest
from mode.utils.times import rate_limit, want_seconds


@pytest.mark.parametrize('input,expected', [
    (1.234, 1.234),
    (1, 1),
    (timedelta(seconds=1.234), 1.234),
    (None, None),
])
def test_want_seconds(input, expected):
    assert want_seconds(input) == expected


@pytest.mark.asyncio
async def test_rate_limit():
    time_start = monotonic()
    x = 0
    bucket = rate_limit(10, 1.0)
    for _ in range(20):
        async with bucket:
            x += 1
    spent = monotonic() - time_start
    assert spent > 1.0


@pytest.mark.asyncio
async def test_pour():
    bucket = rate_limit(10, 1.0, raises=None)
    for _x in range(10):
        assert bucket.pour()
        await asyncio.sleep(0.1)
    assert any(not bucket.pour() for i in range(10))
    assert any(not bucket.pour() for i in range(10))
    assert any(not bucket.pour() for i in range(10))
    await asyncio.sleep(0.4)
    assert bucket.pour()


@pytest.mark.asyncio
async def test_rate_limit_raising():
    bucket = rate_limit(10, 1.0, raises=KeyError)

    for _ in range(10):
        async with bucket:
            await asyncio.sleep(0.1)

    with pytest.raises(KeyError):
        for _ in range(20):
            async with bucket:
                pass
