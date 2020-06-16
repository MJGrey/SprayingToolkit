import asyncio
import pytest
import os
from sprayingtoolkit.modules.o365.sprayers.msol import MSOLSpray


@pytest.mark.asyncio
async def test_o365_sprayers(
    fake_username, fake_password, fake_usernames_file, fake_passwords_file
):
    msol = MSOLSpray()
    msol.interval = "0:00:15"
    msol.auth_jitter = 15

    # await msol.start(fake_username, fake_password)
    # await msol.start(fake_usernames_file, fake_password)
    await msol.start(fake_usernames_file, fake_passwords_file)
    await msol.shutdown()
