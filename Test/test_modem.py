# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from unittest.mock         import MagicMock, AsyncMock
from KeeneticPy.Libs.Modem import find_cellular_interface, extract_cellular_stats, get_modem_info, get_sms_messages, send_sms, send_ussd
import asyncio

def test_find_cellular_interface():
    interfaces = {
        "GigabitEthernet0/0" : {"type" : "Ethernet", "description" : "LAN"},
        "UsbQmi0"            : {"type" : "Cellular", "description" : "4G Dongle"},
        "Wireguard0"         : {"type" : "Wireguard", "description" : "VPN"}
    }
    assert find_cellular_interface(interfaces) == "UsbQmi0"
    assert find_cellular_interface({"ISP" : {"type" : "Ethernet"}}) is None

def test_extract_cellular_stats():
    raw_details = {
        "interface-name" : "UsbQmi0",
        "state"          : "up",
        "connected"      : True,
        "operator"       : "Turkcell",
        "technology"     : "LTE",
        "band"           : 3,
        "signal"         : 85,
        "rsrp"           : -92,
        "rsrq"           : -8,
        "sinr"           : 15
    }
    stats = extract_cellular_stats(raw_details)
    assert stats["operator"] == "Turkcell"
    assert stats["rsrp"] == -92
    assert stats["technology"] == "LTE"

def test_get_modem_info():
    mock_router                        = MagicMock()
    mock_router.interface.return_value = {
        "UsbLte0"        : {
            "interface-name" : "UsbLte0",
            "operator"       : "Vodafone",
            "type"           : "Cellular"
        }
    }
    info = get_modem_info(mock_router)
    assert info["operator"] == "Vodafone"

def test_async_get_modem_info():
    async def run():
        mock_router                        = AsyncMock()
        mock_router.interface.return_value = {
            "Cellular0"      : {
                "interface-name" : "Cellular0",
                "operator"       : "Turk Telekom",
                "type"           : "Cellular"
            }
        }
        info = await get_modem_info(mock_router)
        assert info["operator"] == "Turk Telekom"
    asyncio.run(run())

def test_sms_operations():
    mock_router                  = MagicMock()
    mock_router.rci.return_value = {
        "show"     : {
            "sms"      : {
                "messages" : {
                    "message"  : [{"phone" : "+905551234567", "text" : "Test SMS", "date" : "2026-09-11"}]
                }
            }
        }
    }
    msgs = get_sms_messages(mock_router)
    assert len(msgs) == 1
    assert msgs[0]["phone"] == "+905551234567"

    assert send_sms(mock_router, "+905551234567", "Hello") is True
    mock_router.rci.return_value = {"sms" : {"ussd" : {"response" : "Balance: 50 TL"}}}
    assert send_ussd(mock_router, "*100#") == "Balance: 50 TL"

def test_async_sms_operations():
    async def run():
        mock_router = AsyncMock()
        mock_router.rci.return_value = {"show" : {"sms" : {"messages" : {"message" : []}}}}
        msgs = await get_sms_messages(mock_router)
        assert msgs == []

        assert await send_sms(mock_router, "+90555", "Hi") is True
        mock_router.rci.return_value = {"sms" : {"ussd" : {"response" : "OK"}}}
        assert await send_ussd(mock_router, "*123#") == "OK"

    asyncio.run(run())
