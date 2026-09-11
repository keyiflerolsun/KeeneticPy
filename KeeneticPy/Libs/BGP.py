# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from httpx      import AsyncClient
from .Helpers   import cidr2mask
from contextlib import suppress
import asyncio
import concurrent.futures
import ipaddress
import socket

def run_sync(coro):
    """Run an async coroutine synchronously, supporting running event loops."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(asyncio.run, coro).result()
    return asyncio.run(coro)

async def _async_domain2ip(domain:str, client:AsyncClient=None) -> dict:
    """Resolve domain to IP addresses and subnets via DoH asynchronously."""
    domain       = domain.strip().lower()
    ips          = set()
    close_client = False

    if client is None:
        client       = AsyncClient(timeout=5.0)
        close_client = True

    try:
        with suppress(Exception):
            resp = await client.get(
                url     = f"https://1.1.1.1/dns-query?name={domain}&type=A",
                headers = {"Accept" : "application/dns-json"}
            )
            if resp.status_code == 200:
                for record in resp.json().get("Answer", []):
                    if record.get("type") == 1:
                        ips.add(record.get("data"))
    finally:
        if close_client:
            await client.aclose()

    if not ips:
        with suppress(Exception):
            for info in socket.getaddrinfo(domain, None, socket.AF_INET):
                ips.add(info[4][0])

    sorted_ips = sorted(list(ips))
    subnets    = []
    if sorted_ips:
        try:
            nets    = [ipaddress.ip_network(f"{ip}/32") for ip in sorted_ips]
            subnets = [str(net) for net in ipaddress.collapse_addresses(nets)]
        except Exception:
            subnets = [f"{ip}/32" for ip in sorted_ips]

    return {
        "domain"    : domain,
        "ipler"     : sorted_ips or None,
        "subnetler" : subnets or None
    }

def domain2ip(domain:str, client:AsyncClient=None) -> dict:
    """Resolve domain to IP addresses and subnets (supports both sync and await)."""
    if client is not None:
        return _async_domain2ip(domain, client=client)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        return _async_domain2ip(domain)
    return run_sync(_async_domain2ip(domain))

async def _async_asn2cidr(asn:str|int, client:AsyncClient=None) -> dict:
    """Fetch announced IPv4 prefixes and company name for an ASN asynchronously."""
    try:
        asn_num = int(str(asn).upper().replace("AS", "").strip())
    except ValueError:
        return {}

    company      = f"AS{asn_num}"
    prefixes     = []
    close_client = False

    if client is None:
        client       = AsyncClient(timeout=10.0)
        close_client = True

    try:
        with suppress(Exception):
            info_resp = await client.get(f"https://stat.ripe.net/data/as-overview/data.json?resource=AS{asn_num}")
            if info_resp.status_code == 200:
                company = info_resp.json().get("data", {}).get("holder") or company

            prefix_resp = await client.get(f"https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS{asn_num}")
            if prefix_resp.status_code == 200:
                prefixes = [
                    p["prefix"] for p in prefix_resp.json().get("data", {}).get("prefixes", [])
                    if ":" not in p.get("prefix", "")
                ]
    finally:
        if close_client:
            await client.aclose()

    return {
        "company"  : company,
        "website"  : None,
        "prefixes" : sorted(list(set(prefixes)))
    }

def asn2cidr(asn:str|int, client:AsyncClient=None) -> dict:
    """Fetch announced IPv4 prefixes and company name for an ASN (supports both sync and await)."""
    if client is not None:
        return _async_asn2cidr(asn, client=client)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        return _async_asn2cidr(asn)
    return run_sync(_async_asn2cidr(asn))

async def _async_ip2asname(ip:str, client:AsyncClient=None) -> str:
    """Resolve IP address to its Autonomous System name asynchronously."""
    close_client = False
    if client is None:
        client       = AsyncClient(timeout=6.0)
        close_client = True
    try:
        with suppress(Exception):
            resp = await client.get(f"https://stat.ripe.net/data/network-info/data.json?resource={ip}")
            if resp.status_code == 200:
                asns = resp.json().get("data", {}).get("asns", [])
                if asns:
                    as_info = await client.get(f"https://stat.ripe.net/data/as-overview/data.json?resource=AS{asns[0]}")
                    if as_info.status_code == 200:
                        return as_info.json().get("data", {}).get("holder") or f"AS{asns[0]}"
    finally:
        if close_client:
            await client.aclose()
    return ""

def ip2asname(ip:str, client:AsyncClient=None) -> str:
    """Resolve IP address to its Autonomous System name (supports both sync and await)."""
    if client is not None:
        return _async_ip2asname(ip, client=client)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        return _async_ip2asname(ip)
    return run_sync(_async_ip2asname(ip))

class BGPTools:
    """Helper class for BGP and DNS lookups."""
    cidr2mask = staticmethod(cidr2mask)
    domain2ip = staticmethod(domain2ip)
    asn2cidr  = staticmethod(asn2cidr)
    ip2asname = staticmethod(ip2asname)
