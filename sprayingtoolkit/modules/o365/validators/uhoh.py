import httpx
import logging
from sprayingtoolkit.utils.common import gen_random_string
from sprayingtoolkit.base import BaseValidator

log = logging.getLogger("atomizer.modules.o365.validators")


class UhOh365(BaseValidator):
    def __init__(self, target, interval="1:00:00"):
        self.domain = target
        self.target = target
        self.interval = interval
        self.client = httpx.AsyncClient(verify=False, http2=True, trust_env=True)

        self.user_agent = (
            "Microsoft Office/16.0 (Windows NT 10.0; Microsoft Outlook 16.0.12026; Pro)"
        )
        self.headers = {"User-Agent": self.user_agent, "Accept": "application/json"}

    async def shutdown(self):
        await self.client.aclose()

    async def validate(self, email):
        r = await self.client.get(
            f"https://outlook.office365.com/autodiscover/autodiscover.json/v1.0/{email}?Protocol=Autodiscoverv1",
            headers=self.headers,
            allow_redirects=False,
        )
        if r.status_code == 200 and "X-MailboxGuid" in r.headers.keys():
            log.info(f"{email} => Valid")
        elif r.status_code == 302:
            if (await self.is_hosted_on_o365(self.domain)) == True and "outlook.office365.com" not in r.text:
                log.info(f"{email} => Valid")
            else:
                log.info(f"{email} => Invalid")

    async def is_hosted_on_o365(self, domain):
        junk_user = gen_random_string(20)
        r = await self.client.get(
            f"https://outlook.office365.com/autodiscover/autodiscover.json/v1.0/{junk_user}@{domain}?Protocol=Autodiscoverv1",
            headers=self.headers,
            allow_redirects=False,
        )
        if "outlook.office365.com" in r.text:
            return True
        return False
