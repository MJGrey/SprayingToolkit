import asyncio
import httpx
import logging
import urllib.parse as urlparse
from json.decoder import JSONDecodeError
from httpcore._exceptions import ConnectError
from sprayingtoolkit.exceptions import AutodiscoverUrlNotFound
from sprayingtoolkit.models import HostingLocation
from sprayingtoolkit.exceptions import LyncBaseUrlNotFound

log = logging.getLogger("atomizer.modules.lync.recon")


class LyncRecon:
    def __init__(self, target):
        self.target = target
        self.domain = target
        self.client = httpx.AsyncClient(verify=False, trust_env=True, http2=True)

    async def start(self):
        internal_hostname = None

        autodiscover_url = await self.get_autodiscover_url(self.domain)
        log.debug(f"Using Lync/S4B autodiscover URL: {autodiscover_url}")

        base_url = await self.get_base_url(autodiscover_url)
        auth_url = urlparse.urljoin(
            "/".join(base_url.split("/")[0:3]), "/WebTicket/oauthtoken"
        )

        log.debug(f"Lync/S4B base url: {base_url}")
        log.debug(f"Lync/S4B auth url: {auth_url}")

        hosting_location = await self.get_hosting_location(base_url)
        if hosting_location == HostingLocation.internal:
            internal_hostname = await self.get_internal_hostname(base_url)

        return {
            "target": self.target,
            "autodiscover_url": autodiscover_url,
            "base_url": base_url,
            "auth_url": auth_url,
            "hosting_location": hosting_location,
            "internal_hostname": internal_hostname,
        }

    async def shutdown(self):
        await self.client.aclose()

    async def get_hosting_location(self, base_url):
        if "online.lync.com" in base_url:
            log.info("Target appears to be using O365")
            return HostingLocation.O365

        log.info("Target appears to be hosting Lync/S4B internally")
        return HostingLocation.internal

    async def get_autodiscover_url(self, domain):
        urls = [
            f"https://lyncdiscover.{domain}",
            f"https://lyncdiscoverinternal.{domain}",
        ]

        tasks = [self.client.get(url) for url in urls]

        for r in await asyncio.gather(*tasks, return_exceptions=True):
            if not isinstance(r, ConnectError):
                return str(r.url)

        raise AutodiscoverUrlNotFound(
            f"Unable to find autodiscover url for '{domain}' target does not seem to be using Lync/S4B"
        )

    # https://github.com/mdsecresearch/LyncSniper/blob/master/LyncSniper.ps1#L259
    async def get_base_url(self, url: str) -> str:
        log.debug(f"Resolving Lync/S4B base URL from: {url}")
        r = await self.client.get(url, headers={"Content-Type": "application/json"})
        # log.debug(r.status_code, r.headers, r.text)
        try:
            data = r.json()
        except JSONDecodeError:
            raise LyncBaseUrlNotFound(
                f"Unable to find Lync/S4B base url from '{url}', target is probably not using Lync/S4B"
            )
        else:
            if "user" in data["_links"]:
                return data["_links"]["user"]["href"]

            return await self.get_base_url(data["_links"]["redirect"]["href"])

    async def get_internal_hostname(self, url):
        r = await self.client.get(url)
        return r.headers["X-MS-Server-Fqdn"]
