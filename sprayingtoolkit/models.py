from enum import Enum
from typing import Union, List
from pydantic import BaseModel, HttpUrl, IPvAnyAddress

class O365SprayMethods(str, Enum):
    msol = "msol"

class O365ValidationMethods(str, Enum):
    uhoh365 = "uhoh365"

class HostingLocation(str, Enum):
    internal = 'internal'
    O365 = 'O365'
    unknown = 'unknown'

class Modules(str, Enum):
    lync = 'lync'
    o365 = 'o365'
    owa = 'owa'

class OwaReconData(BaseModel):
    autodiscover_url: HttpUrl
    hosting_location: HostingLocation
    internal_ips: List[Union[IPvAnyAddress, None]]
    netbios_domain: Union[str, None]
    target: str

class LyncReconData(BaseModel):
    autodiscover_url: HttpUrl
    hosting_location: HostingLocation
    auth_url: HttpUrl
    base_url: HttpUrl
    internal_hostname: str
    target: str

class O365ReconData(BaseModel):
    pass

class SprayParams(BaseModel):
    pass

class ValidateParams(BaseModel):
    pass
