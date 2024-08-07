# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from Kekik  import Domain2IP
from httpx  import Client
from parsel import Selector

def asn2cidr(asn:int) -> dict:
    if not isinstance(asn, int):
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

def domain2ip(domain):
    return Domain2IP(domain).bilgi