import asyncio
import pytest
import time
from decimal import Decimal, getcontext, ROUND_DOWN
from sprayingtoolkit.utils.credentials import automatic_cred_generator
from sprayingtoolkit.utils.time import countdown_timer


@pytest.mark.asyncio
async def test_automatic_cred_generator(fake_usernames_file, fake_username):
    n = 0
    async for _ in automatic_cred_generator(fake_usernames_file):
        n += 1
    assert n == 100

    n = 0
    user = ""
    async for u in automatic_cred_generator(fake_username):
        n += 1
        user = u

    assert n == 1
    assert user == fake_username


@pytest.mark.asyncio
async def test_countdown_timer():
    getcontext().prec = 2
    getcontext().rounding = ROUND_DOWN

    started_at = time.monotonic()
    await countdown_timer("0:0:5")
    total = time.monotonic() - started_at

    assert Decimal(total) < Decimal(6)
