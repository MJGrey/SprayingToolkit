import asyncio
import httpx
import logging
from sprayingtoolkit.utils.common import gen_random_string
from sprayingtoolkit.models import HostingLocation

log = logging.getLogger("atomizer.modules.o365.recon")

class O365Recon:
    def __init__(self, target):
        self.domain = target
        self.target = target
        self.client = httpx.AsyncClient(verify=False, http2=True, trust_env=True)

        self.user_agent = (
            "Microsoft Office/16.0 (Windows NT 10.0; Microsoft Outlook 16.0.12026; Pro)"
        )
        self.headers = {"User-Agent": self.user_agent, "Accept": "application/json"}

    async def shutdown(self):
        await self.client.aclose()

    async def start(self):
        hosting_location = await self.get_hosting_location(self.domain)

        return {
            "hosting_location": hosting_location
        }

    async def get_hosting_location(self, domain):
        junk_user = gen_random_string(20)
        r = await self.client.get(
            f"https://outlook.office365.com/autodiscover/autodiscover.json/v1.0/{junk_user}@{domain}?Protocol=Autodiscoverv1",
            headers=self.headers,
            allow_redirects=False,
        )

        if "outlook.office365.com" in r.text:
            log.info("Target uses o365")
            return HostingLocation.O365
        
        return HostingLocation.unknown
