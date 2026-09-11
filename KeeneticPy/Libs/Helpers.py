# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from zipfile    import ZipFile, ZIP_DEFLATED
from contextlib import suppress
import asyncio
import inspect
import ipaddress
import os
import re
import unicodedata

TR_MAP = str.maketrans("ıİğĞüÜşŞöÖçÇ", "iIgGuUsSoOcC")

def slugify(value:str, allow_unicode:bool=False) -> str:
    """Convert text to a URL/filename-friendly slug."""
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = unicodedata.normalize("NFKD", value.translate(TR_MAP)).encode("ascii", "ignore").decode("ascii")

    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s_]+", "-", value).strip("-")

def cidr2mask(cidr:str) -> str:
    """Convert CIDR notation (e.g. 1.1.1.0/24) to subnet mask (e.g. 255.255.255.0)."""
    with suppress(Exception):
        return str(ipaddress.IPv4Network(cidr.strip(), strict=False).netmask)

    ip, prefix = cidr.strip().split("/")
    prefix     = int(prefix)
    mask       = (0xFFFFFFFF >> (32 - prefix)) << (32 - prefix)
    return f"{(mask >> 24) & 0xFF}.{(mask >> 16) & 0xFF}.{(mask >> 8) & 0xFF}.{mask & 0xFF}"

def mask2cidr(mask:str) -> int:
    """Convert subnet mask (e.g. 255.255.255.0) to CIDR prefix length (e.g. 24)."""
    return ipaddress.IPv4Network(f"0.0.0.0/{mask}").prefixlen

def format_bytes(byte_count:int|float) -> str:
    """Convert bytes into human-readable representation."""
    if not byte_count or byte_count <= 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    i     = 0
    val   = float(byte_count)
    while val >= 1024 and i < len(units) - 1:
        val /= 1024
        i   += 1

    return f"{val:.1f} {units[i]}"

def build_route_payload(comment:str=None, host:str=None, network:str=None, mask:str=None, interface:str="Wireguard0", no:bool=False) -> dict:
    """Build Keenetic RCI static route payload."""
    payload = {"interface" : interface}
    if comment:
        payload["comment"] = comment
    if host:
        payload["host"] = host
    elif network and mask:
        payload["network"] = network
        payload["mask"]    = mask
    else:
        raise ValueError("Please provide 'host' or ('network' and 'mask').")

    if no:
        payload["no"] = True
    return payload

def extract_wan_ips(data:dict) -> dict:
    """Extract WAN IPv4 and IPv6 addresses from RCI response."""
    ipv4 = None
    ipv6 = None
    with suppress(Exception):
        ifaces = data.get("show", {}).get("interface", {})
        for name in ["PPPoE0", "ISP", "GigabitEthernet0/Vlan2"]:
            if name in ifaces and ifaces[name].get("address"):
                ipv4 = ifaces[name]["address"]
                break

        ipv6_list = data.get("show", {}).get("ipv6", {}).get("addresses", {}).get("address", [])
        for addr in ipv6_list:
            if addr.get("address"):
                ipv6 = addr["address"]
                break

    return {"ipv4" : ipv4, "ipv6" : ipv6}

def save_backup_archive(zip_path:str, fw_bytes:bytes=None, cfg_bytes:bytes=None, max_backups:int=5, target_dir:str="."):
    """Save firmware and startup-config to zip archive and rotate older backups."""
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
        if fw_bytes:
            archive.writestr("firmware.bin", fw_bytes)
        if cfg_bytes:
            archive.writestr("startup-config.txt", cfg_bytes)

    with suppress(Exception):
        prefix  = os.path.basename(zip_path).split("_")[0]
        backups = sorted(
            [os.path.join(target_dir, f) for f in os.listdir(target_dir) if f.startswith(prefix) and f.endswith(".zip")],
            key     = os.path.getmtime,
            reverse = True
        )
        for old_file in backups[max_backups:]:
            os.remove(old_file)

def call_router(router, method:str, *args, **kwargs):
    """Call a router method transparently supporting both sync Keenetic and async AsyncKeenetic."""
    target = router.__dict__.get("_async_client", router)
    res    = getattr(target, method)(*args, **kwargs)
    if inspect.isawaitable(res):
        if getattr(router, "is_async", False):
            return res
        if hasattr(router, "_run"):
            return router._run(res)
        return asyncio.run(res)
    return res

def call_rci_status(router, payload:dict|list) -> bool:
    """Execute RCI payload and return boolean success for both sync and async routers."""
    target = router.__dict__.get("_async_client", router)
    try:
        res = target.rci(payload)
        if inspect.isawaitable(res):
            if getattr(router, "is_async", False):
                async def _wrap():
                    with suppress(Exception):
                        await res
                        return True
                    return False
                return _wrap()
            with suppress(Exception):
                if hasattr(router, "_run"):
                    router._run(res)
                else:
                    asyncio.run(res)
                return True
            return False
        return True
    except Exception:
        return False
