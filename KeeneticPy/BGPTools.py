# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from Kekik  import Domain2IP
from httpx  import Client
from parsel import Selector

def cidr2mask(cidr:str) -> str:
    ip, prefix = cidr.split("/")
    prefix     = int(prefix)
    mask       = (0xFFFFFFFF >> (32 - prefix)) << (32 - prefix)

    return f"{(mask >> 24) & 0xFF}.{(mask >> 16) & 0xFF}.{(mask >> 8) & 0xFF}.{mask & 0xFF}"

def asn2cidr(asn:str|int) -> dict:
    try:
        asn = int(asn)
    except ValueError:
        return {}

    oturum = Client()
    istek  = oturum.get(f"https://bgp.tools/as/{asn}?show-low-vis#prefixes")
    if istek.status_code != 200:
        return {}

    secici = Selector(istek.text)

    return {
        "company"  : secici.css("p#network-name::text").get(),
        "website"  : secici.css("p#network-number a::attr(href)").get(),
        "prefixes" : [
            cidr.xpath("./@id").get().split("-")[-1]
                for cidr in secici.xpath("//table[@id='fhTable']//tr[contains(@id, '/')]")
                    if "::" not in cidr.xpath("./@id").get().split("-")[-1]
        ]
    }

def domain2ip(domain:str) -> dict:
    return Domain2IP(domain).bilgi