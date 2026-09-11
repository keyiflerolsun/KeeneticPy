# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from httpx      import Client, AsyncClient
from .Helpers   import call_router
from contextlib import suppress
import asyncio
import inspect
import ipaddress

def parse_route_entries(text:str) -> list[dict]:
    """Parse CIDR subnets and single host IPs from multi-line text or file contents."""
    entries = []
    seen    = set()

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "//", ";")):
            continue

        parts   = line.split(maxsplit=1)
        target  = parts[0].strip()
        comment = parts[1].strip("# ;//") if len(parts) > 1 else ""

        with suppress(Exception):
            if "/" in target:
                net = ipaddress.IPv4Network(target, strict=False)
                key = str(net)
                if key not in seen:
                    seen.add(key)
                    entries.append({
                        "network" : str(net.network_address),
                        "mask"    : str(net.netmask),
                        "comment" : comment,
                        "cidr"    : key
                    })
            else:
                ip  = ipaddress.IPv4Address(target)
                key = str(ip)
                if key not in seen:
                    seen.add(key)
                    entries.append({
                        "host"    : key,
                        "comment" : comment,
                        "cidr"    : f"{key}/32"
                    })

    return entries

async def _async_fetch_route_text(source:str, client:AsyncClient=None) -> str:
    """Fetch route text from URL or local file asynchronously."""
    if source.startswith(("http://", "https://")):
        close_client = False
        if client is None:
            client       = AsyncClient(timeout=15.0)
            close_client = True
        try:
            resp = await client.get(source)
            resp.raise_for_status()
            return resp.text
        finally:
            if close_client:
                await client.aclose()

    with open(source, "r", encoding="utf-8") as f:
        return f.read()

def fetch_route_text(source:str, client:AsyncClient=None) -> str:
    """Fetch route text from HTTP/HTTPS URL or local filesystem path (supports both sync and await)."""
    if not source.startswith(("http://", "https://")):
        with open(source, "r", encoding="utf-8") as f:
            return f.read()

    if client is not None:
        return _async_fetch_route_text(source, client=client)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        return _async_fetch_route_text(source)

    with Client(timeout=15.0) as sync_client:
        resp = sync_client.get(source)
        resp.raise_for_status()
        return resp.text

def sync_static_routes(router, new_entries:list[dict], interface:str="Wireguard0", tag:str="AutoSync"):
    """Synchronize router static routes with a list of entries, pruning stale tagged routes."""
    tag_prefix = f"[{tag}]"

    def _process_routes(current_routes, add_fn, del_fn, is_async:bool):
        existing_tagged = {}
        for r in current_routes:
            comment = r.get("comment", "")
            if tag_prefix in comment or comment == tag:
                key = (r.get("network"), r.get("mask")) if r.get("network") else r.get("host")
                existing_tagged[key] = r

        desired_keys = set()
        added        = []
        removed      = []

        if is_async:
            async def _do_sync():
                for entry in new_entries:
                    key = (entry.get("network"), entry.get("mask")) if entry.get("network") else entry.get("host")
                    desired_keys.add(key)
                    if key not in existing_tagged:
                        full_comm = f"{tag_prefix} {entry.get('comment', '')}".strip()
                        if await add_fn(
                            comment   = full_comm,
                            host      = entry.get("host"),
                            network   = entry.get("network"),
                            mask      = entry.get("mask"),
                            interface = interface
                        ):
                            added.append(entry.get("cidr"))

                for key, route_data in existing_tagged.items():
                    if key not in desired_keys:
                        if await del_fn(**route_data):
                            removed.append(key if isinstance(key, str) else f"{key[0]}/{key[1]}")

                return {"tag" : tag, "added" : added, "removed" : removed, "total" : len(desired_keys)}
            return _do_sync()

        for entry in new_entries:
            key = (entry.get("network"), entry.get("mask")) if entry.get("network") else entry.get("host")
            desired_keys.add(key)
            if key not in existing_tagged:
                full_comm = f"{tag_prefix} {entry.get('comment', '')}".strip()
                if add_fn(
                    comment   = full_comm,
                    host      = entry.get("host"),
                    network   = entry.get("network"),
                    mask      = entry.get("mask"),
                    interface = interface
                ):
                    added.append(entry.get("cidr"))

        for key, route_data in existing_tagged.items():
            if key not in desired_keys:
                if del_fn(**route_data):
                    removed.append(key if isinstance(key, str) else f"{key[0]}/{key[1]}")

        return {"tag" : tag, "added" : added, "removed" : removed, "total" : len(desired_keys)}

    routes_val = call_router(router, "get_static_routes")
    if inspect.isawaitable(routes_val):
        async def _async_wrapper():
            resolved_routes = await routes_val
            target          = router.__dict__.get("_async_client", router)
            return await _process_routes(resolved_routes, target.add_static_route, target.del_static_route, is_async=True)
        return _async_wrapper()

    target = router.__dict__.get("_async_client", router)
    return _process_routes(routes_val, target.add_static_route, target.del_static_route, is_async=False)
