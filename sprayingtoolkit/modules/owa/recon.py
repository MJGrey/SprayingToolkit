import ssl
import httpx
import asyncio
import logging
import http.client
import functools
from pydantic import HttpUrl
from typing import List, Union
from urllib.parse import urlparse
from httpcore._exceptions import ConnectError
from sprayingtoolkit.utils.ntlmdecoder import ntlmdecode
from sprayingtoolkit.utils.common import coro, make_async
from sprayingtoolkit.exceptions import AutodiscoverUrlNotFound
from sprayingtoolkit.models import HostingLocation

log = logging.getLogger("atomizer.modules.owa.recon")


class OwaRecon:
    def __init__(self, target):
        self.target = target
        self.domain = target
        self.headers = {}
        self.client = httpx.AsyncClient(
            verify=False, trust_env=True, http2=True, headers=self.headers
        )

    async def start(self) -> None:
        netbios_domain = None
        internal_ips = []

        autodiscover_url, hosting_location = await asyncio.gather(
            self.get_autodiscover_url(self.domain),
            self.get_hosting_location(self.domain),
        )

        log.debug(f"Using OWA autodiscover URL: {autodiscover_url}")

        if hosting_location == HostingLocation.internal:
            netbios_domain, internal_ips = await asyncio.gather(
                self.get_internal_domain(autodiscover_url),
                self.get_internal_ips(autodiscover_url),
            )

        return {
            "target": self.target,
            "hosting_location": hosting_location,
            "autodiscover_url": autodiscover_url,
            "netbios_domain": netbios_domain,
            "internal_ips": internal_ips,
        }

    async def shutdown(self):
        await self.client.aclose()

    async def get_hosting_location(self, domain: str) -> HostingLocation:
        # https://github.com/sensepost/ruler/blob/master/ruler.go#L140
        o365_owa_url = f"https://login.microsoftonline.com/{domain}/.well-known/openid-configuration"
        r = await self.client.get(o365_owa_url)
        if r.status_code == 400:
            log.info("Target appears to be hosting OWA internally")
            return HostingLocation.internal

        elif r.status_code == 200:
            log.info("Target appears to be using Office365")
            return HostingLocation.O365

        return HostingLocation.unknown

    @make_async
    def get_internal_ips(self, autodiscover_url: HttpUrl) -> List[str]:
        """
        Gets the internal IP of MS Exchange systems (e.g. OWA, CAS), only works if they're internally hosted.
        http://foofus.net/?p=758

        We have to use http.client here cause httpx (or really any other library) doesn't support sending HTTP 1.0 requests
        """
        internal_ips = []

        url = urlparse(autodiscover_url)
        conn = (
            http.client.HTTPSConnection(
                url.netloc, context=ssl._create_unverified_context()
            )
            if url.scheme == "https"
            else http.client.HTTPConnection(url.netloc)
        )

        conn._http_vsn = 10
        conn._http_vsn_str = "HTTP/1.0"
        conn.request("GET", url.path)
        r = conn.getresponse()

        location_header = r.headers.get("location")
        auth_headers = r.headers.get_all("www-authenticate")
        if location_header:
            internal_ips.append(urlparse(location_header).netloc)

        if auth_headers:
            basic_header = list(
                filter(lambda h: h.lower().startswith("basic realm"), auth_headers)
            )[0]
            internal_ips.append(basic_header.split("=")[1][1:-1])

        log.debug(f"Got internal IP(s): {internal_ips}")
        return internal_ips

    async def get_autodiscover_url(self, domain: str) -> str:
        log.info(f"Attempting to find autodiscover url for domain '{domain}'")
        urls = [
            f"https://autodiscover.{domain}/autodiscover/autodiscover.xml",
            f"http://autodiscover.{domain}/autodiscover/autodiscover.xml",
            f"https://{domain}/autodiscover/autodiscover.xml",
        ]

        tasks = [
            self.client.get(url, headers={"Content-Type": "text/xml"}) for url in urls
        ]

        for r in await asyncio.gather(*tasks, return_exceptions=True):
            if not isinstance(r, ConnectError) and r.status_code in [401, 403]:
                return str(r.url)

        raise AutodiscoverUrlNotFound(
            f"Unable to find autodiscover url for '{domain}' target does not seem to be using OWA"
        )

    async def get_internal_domain(self, url: HttpUrl) -> str:
        # Stolen from https://github.com/dafthack/MailSniper
        auth_header = {
            "Authorization": "NTLM TlRMTVNTUAABAAAAB4IIogAAAAAAAAAAAAAAAAAAAAAGAbEdAAAADw=="
        }
        try:
            r = await self.client.post(url, headers=auth_header)
            if r.status_code == 401:
                ntlm_info = ntlmdecode(r.headers["WWW-Authenticate"])
                internal_domain = ntlm_info["NetBIOS_Domain_Name"]
                log.debug(f"Got internal domain name: {internal_domain}")

                return internal_domain
        except Exception as e:
            log.debug(f"Failed getting internal domain name: {e}")
