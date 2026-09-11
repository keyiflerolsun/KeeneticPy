# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from .Helpers import call_rci_status

def set_speed_limit(router, mac:str, rx_kbps:int=0, tx_kbps:int=0) -> bool:
    """Set bandwidth limit (shaping) in kbps for a device by MAC address."""
    mac           = mac.strip().lower()
    shape_payload = {"rx" : rx_kbps, "tx" : tx_kbps} if (rx_kbps > 0 or tx_kbps > 0) else {"no" : True}
    payload       = [
        {"ip"     : {"hotspot" : {"host" : {"mac" : mac, "shape" : shape_payload}}}},
        {"system" : {"configuration" : {"save" : {}}}}
    ]
    return call_rci_status(router, payload)

def set_client_access(router, mac:str, permit:bool=True) -> bool:
    """Allow or block network access for a client MAC address."""
    mac     = mac.strip().lower()
    payload = [
        {"ip"     : {"hotspot" : {"host" : {"mac" : mac, "permit" : permit}}}},
        {"system" : {"configuration" : {"save" : {}}}}
    ]
    return call_rci_status(router, payload)

def set_dhcp_binding(router, mac:str, ip:str, name:str=None) -> bool:
    """Set static DHCP reservation lease for a client MAC address."""
    mac          = mac.strip().lower()
    host_payload = {"mac" : mac, "ip" : ip.strip()}
    if name:
        host_payload["name"] = name.strip()

    payload = [
        {"ip"     : {"dhcp" : {"host" : host_payload}}},
        {"system" : {"configuration" : {"save" : {}}}}
    ]
    return call_rci_status(router, payload)

def find_client(hosts_data:dict, identifier:str) -> dict | None:
    """Find client details by IP, MAC, or name from hosts response."""
    identifier = identifier.strip().lower()
    for host in hosts_data.get("host", []):
        mac  = host.get("mac", "").lower()
        ip   = host.get("ip", "").lower()
        name = (host.get("name") or host.get("hostname") or "").lower()
        if identifier in (mac, ip, name):
            return host
    return None
