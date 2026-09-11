# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from httpx       import AsyncClient
from hashlib     import md5, sha256
from datetime    import datetime
from .Exceptions import KeeneticAuthError, KeeneticRCIError, KeeneticConnectionError
from ..Libs      import slugify, cidr2mask, build_route_payload, extract_wan_ips, save_backup_archive, asn2cidr, domain2ip
import logging
import os
import re

logger = logging.getLogger("KeeneticPy.async")

class AsyncKeenetic:
    """Asynchronous KeeneticOS RCI API Client."""
    is_async = True

    def __init__(self, user:str="admin", password:str="", panel:str="http://192.168.1.1", timeout:float=10.0, verify:bool=False, transport=None):
        self.user      = user
        self.password  = password
        self.panel     = panel.rstrip("/")
        self.rci_url   = f"{self.panel}/rci/"
        self.timeout   = timeout
        self.verify    = verify
        self.transport = transport
        self.oturum    = AsyncClient(timeout=timeout, verify=verify, transport=transport)
        self._yetkili  = False
        self._yetki    = False

    async def __aenter__(self):
        await self.authenticate()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close asynchronous HTTP session."""
        await self.oturum.aclose()

    async def authenticate(self, user:str=None, password:str=None) -> bool:
        """Authenticate using Keenetic NDM challenge-response protocol."""
        user     = user or self.user
        password = password or self.password
        try:
            req = await self.oturum.get(f"{self.panel}/auth")
            if req.status_code == 200:
                self._yetkili = True
                self._yetki   = True
                return True

            realm     = req.headers.get("X-NDM-Realm")
            challenge = req.headers.get("X-NDM-Challenge")
            if not realm or not challenge:
                raise KeeneticAuthError("Missing challenge-response headers from router.")

            pass_hash = md5(f"{user}:{realm}:{password}".encode("utf-8")).hexdigest()
            auth_hash = sha256(f"{challenge}{pass_hash}".encode("utf-8")).hexdigest()

            resp = await self.oturum.post(
                url  = f"{self.panel}/auth",
                json = {"login" : user, "password" : auth_hash}
            )
            self._yetkili = (resp.status_code == 200)
            self._yetki   = self._yetkili
            if not self._yetkili:
                raise KeeneticAuthError("Invalid username or password.")
            return True
        except KeeneticAuthError:
            raise
        except Exception as e:
            raise KeeneticConnectionError(f"Failed to connect to router panel ({self.panel}): {e}")

    async def rci(self, payload:dict|list) -> dict|list:
        """Execute raw RCI command or batch list."""
        if not self._yetkili:
            await self.authenticate()

        resp = await self.oturum.post(url=self.rci_url, json=payload)
        if resp.status_code != 200:
            raise KeeneticRCIError(f"RCI request failed (Status {resp.status_code}): {resp.text}")
        return resp.json()

    async def system(self) -> dict:
        """Get system status (CPU, RAM, Uptime)."""
        if not self._yetkili:
            await self.authenticate()
        return (await self.oturum.get(f"{self.rci_url}show/system")).json()

    async def version(self) -> dict:
        """Get model, hardware revision and KeeneticOS version."""
        if not self._yetkili:
            await self.authenticate()
        return (await self.oturum.get(f"{self.rci_url}show/version")).json()

    async def interface(self) -> dict:
        """Get status of all network interfaces."""
        if not self._yetkili:
            await self.authenticate()
        return (await self.oturum.get(f"{self.rci_url}show/interface")).json()

    async def get_interface_names(self) -> list[dict]:
        """Get summary list of configured interfaces."""
        ifaces = await self.interface()
        return [
            {"name" : v.get("interface-name"), "type" : v.get("type"), "description" : v.get("description")}
            for k, v in ifaces.items()
            if isinstance(v, dict) and v.get("description")
        ]

    async def hosts(self) -> dict:
        """Get list of connected hotspot clients (LAN / Wi-Fi)."""
        if not self._yetkili:
            await self.authenticate()
        return (await self.oturum.get(f"{self.rci_url}show/ip/hotspot")).json()

    async def dsl_stats(self) -> dict:
        """Get DSL line statistics."""
        return await self.rci({"parse" : "more proc:/driver/ensoc_dsl/dsl_stats"})

    async def mesh_nodes(self) -> list[dict]:
        """Get Keenetic Mesh Wi-Fi System (MWS) member nodes."""
        if not self._yetkili:
            await self.authenticate()
        try:
            data = (await self.oturum.get(f"{self.rci_url}show/mws/member")).json()
            return data if isinstance(data, list) else []
        except Exception:
            return []

    async def reboot_mesh_node(self, cid:str) -> bool:
        """Reboot a specific Mesh Wi-Fi System (MWS) member node by its CID."""
        if not re.fullmatch(r"[\w-]+", cid or ""):
            raise ValueError("Invalid mesh node cid.")
        try:
            await self.rci({"parse" : f"mws member {cid} reboot"})
            return True
        except Exception:
            return False

    async def internet_status(self) -> dict:
        """Get WAN internet connectivity health (gateway/DNS/captive-portal checks)."""
        if not self._yetkili:
            await self.authenticate()
        return (await self.oturum.get(f"{self.rci_url}show/internet/status")).json()

    async def dsl_reset(self) -> bool:
        """Reset DSL interface."""
        try:
            await self.rci([
                {"interface" : {"Dsl0" : {"up" : {"no" : True}}}},
                {"system"    : {"configuration" : {"save" : True}}}
            ])
            await self.rci([
                {"interface" : {"Dsl0" : {"up" : {"no" : False}}}},
                {"system"    : {"configuration" : {"save" : True}}}
            ])
            return True
        except Exception:
            return False

    async def global_ip(self) -> dict:
        """Get WAN IPv4 and IPv6 addresses."""
        data = await self.rci({"show" : {"interface" : {}, "ipv6" : {"addresses" : {}}}})
        return extract_wan_ips(data)

    async def reboot(self) -> bool:
        """Reboot the router."""
        try:
            await self.rci({"system" : {"reboot" : {}}})
            return True
        except Exception:
            return False

    async def wol(self, mac:str) -> bool:
        """Send Wake-on-LAN magic packet to specified MAC address."""
        try:
            await self.rci({"ip" : {"hotspot" : {"wake" : {"mac" : mac}}}})
            return True
        except Exception:
            return False

    async def get_static_routes(self) -> list[dict]:
        """Get list of configured static routes."""
        resp = await self.rci([{"show" : {"rc" : {"ip" : {"route" : {}}}}}] )
        try:
            return resp[0].get("show", {}).get("rc", {}).get("ip", {}).get("route", [])
        except Exception:
            return []

    async def add_static_route(self, comment:str=None, host:str=None, network:str=None, mask:str=None, interface:str="Wireguard0") -> bool:
        """Add static route or policy route to VPN interface."""
        payload = build_route_payload(comment, host, network, mask, interface)
        try:
            await self.rci([{"ip" : {"route" : payload}}, {"system" : {"configuration" : {"save" : {}}}}])
            return True
        except Exception as e:
            logger.error(f"Failed to add static route: {e}")
            return False

    async def del_static_route(self, comment:str=None, host:str=None, network:str=None, mask:str=None, interface:str="Wireguard0") -> bool:
        """Delete static route."""
        payload = build_route_payload(comment, host, network, mask, interface, no=True)
        try:
            await self.rci([{"ip" : {"route" : payload}}, {"system" : {"configuration" : {"save" : {}}}}])
            return True
        except Exception as e:
            logger.error(f"Failed to delete static route: {e}")
            return False

    async def clean_multiple_routes(self) -> int:
        """Remove duplicate static routes."""
        routes  = await self.get_static_routes()
        seen    = set()
        deleted = 0
        for route in routes:
            target = (route.get("network"), route.get("mask")) if route.get("network") else route.get("host")
            if target not in seen:
                seen.add(target)
                continue
            await self.del_static_route(**route)
            deleted += 1
        return deleted

    async def add_route_with_asn(self, asn:str|int, interface:str="Wireguard0") -> list[str]:
        """Add policy routes for all announced IP prefixes of an ASN."""
        asn_data = await asn2cidr(asn, client=self.oturum)
        if not asn_data or not asn_data.get("prefixes"):
            raise ValueError(f"No IP prefixes found for ASN {asn}.")

        added = []
        for prefix in asn_data["prefixes"]:
            net  = prefix.split("/")[0]
            mask = cidr2mask(prefix)
            if await self.add_static_route(comment=asn_data["company"], network=net, mask=mask, interface=interface):
                added.append(prefix)
        return added

    async def add_route_with_domain(self, domain:str, interface:str="Wireguard0") -> list[str]:
        """Resolve domain and add policy routes for its IP addresses or subnets."""
        domain_data = await domain2ip(domain, client=self.oturum)
        if not domain_data or not domain_data.get("ipler"):
            raise ValueError(f"No IP records found for domain {domain}.")

        added = []
        if domain_data.get("subnetler"):
            for subnet in domain_data["subnetler"]:
                net  = subnet.split("/")[0]
                mask = cidr2mask(subnet)
                if await self.add_static_route(comment=domain, network=net, mask=mask, interface=interface):
                    added.append(subnet)
            return added

        for ip in domain_data["ipler"]:
            if await self.add_static_route(comment=domain, host=ip, interface=interface):
                added.append(ip)
        return added

    async def backup(self, max_backups:int=5, target_dir:str=".") -> str:
        """Download firmware and startup-config and save as a rotated zip archive."""
        if not self._yetkili:
            await self.authenticate()

        device    = await self.version()
        today     = datetime.now().strftime("%d-%m-%Y")
        file_name = f"{slugify(device.get('description', 'keenetic'))}_{slugify(device.get('hw_version', 'device'))}_{today}.zip"
        zip_path  = os.path.join(target_dir, file_name)

        fw  = await self.oturum.get(f"{self.panel}/ci/firmware")
        cfg = await self.oturum.get(f"{self.panel}/ci/startup-config")

        save_backup_archive(
            zip_path    = zip_path,
            fw_bytes    = fw.content if fw.status_code == 200 else None,
            cfg_bytes   = cfg.content if cfg.status_code == 200 else None,
            max_backups = max_backups,
            target_dir  = target_dir
        )
        return zip_path
