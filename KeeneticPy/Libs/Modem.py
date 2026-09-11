# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from .Helpers import call_router, call_rci_status
import inspect

def find_cellular_interface(interfaces_data:dict) -> str | None:
    """Detect the name of the active 4G/LTE cellular modem interface."""
    for iface_name, details in interfaces_data.items():
        if not isinstance(details, dict):
            continue
        itype = details.get("type", "")
        desc  = details.get("description", "")
        if any(keyword in iface_name.lower() or keyword in itype.lower() or keyword in desc.lower() for keyword in ["usblte", "usbqmi", "usbmodem", "cellular", "cdcepath"]):
            return iface_name
    return None

def extract_cellular_stats(interface_details:dict) -> dict:
    """Extract cellular signal metrics from interface details."""
    stats = {
        "interface"  : interface_details.get("interface-name") or interface_details.get("id"),
        "state"      : interface_details.get("state"),
        "connected"  : interface_details.get("connected", False),
        "operator"   : interface_details.get("operator") or interface_details.get("spn"),
        "technology" : interface_details.get("technology") or interface_details.get("access-technology"),
        "band"       : interface_details.get("band"),
        "signal"     : interface_details.get("signal"),
        "rssi"       : interface_details.get("rssi"),
        "rsrp"       : interface_details.get("rsrp"),
        "rsrq"       : interface_details.get("rsrq"),
        "sinr"       : interface_details.get("sinr"),
        "cell_id"    : interface_details.get("cell-id") or interface_details.get("cid")
    }
    return {k : v for k, v in stats.items() if v is not None}

def get_modem_info(router, interface:str=None) -> dict:
    """Retrieve signal quality and status of 4G/LTE modem."""
    ifaces = call_router(router, "interface")
    if inspect.isawaitable(ifaces):
        async def _async():
            resolved = await ifaces
            target   = interface or find_cellular_interface(resolved)
            return extract_cellular_stats(resolved[target]) if target and target in resolved else {}
        return _async()

    target = interface or find_cellular_interface(ifaces)
    return extract_cellular_stats(ifaces[target]) if target and target in ifaces else {}

def get_sms_messages(router) -> list[dict]:
    """Retrieve incoming SMS messages from SIM card."""
    payload = {"show" : {"sms" : {"messages" : {}}}}
    res     = call_router(router, "rci", payload)
    if inspect.isawaitable(res):
        async def _async():
            data = await res
            if isinstance(data, dict):
                return data.get("show", {}).get("sms", {}).get("messages", {}).get("message", [])
            if isinstance(data, list) and data:
                return data[0].get("show", {}).get("sms", {}).get("messages", {}).get("message", [])
            return []
        return _async()

    if isinstance(res, dict):
        return res.get("show", {}).get("sms", {}).get("messages", {}).get("message", [])
    if isinstance(res, list) and res:
        return res[0].get("show", {}).get("sms", {}).get("messages", {}).get("message", [])
    return []

def send_sms(router, phone:str, text:str) -> bool:
    """Send SMS message via cellular modem."""
    payload = {"sms" : {"send" : {"phone" : phone.strip(), "text" : text.strip()}}}
    return call_rci_status(router, payload)

def send_ussd(router, code:str) -> str | None:
    """Execute USSD command (e.g. *100#) and return text response."""
    payload = {"sms" : {"ussd" : {"request" : code.strip()}}}
    res     = call_router(router, "rci", payload)
    if inspect.isawaitable(res):
        async def _async():
            data = await res
            return data.get("sms", {}).get("ussd", {}).get("response") if isinstance(data, dict) else None
        return _async()

    return res.get("sms", {}).get("ussd", {}).get("response") if isinstance(res, dict) else None
