# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from unittest.mock           import MagicMock, AsyncMock
from KeeneticPy.Libs.Clients import set_speed_limit, set_client_access, set_dhcp_binding, find_client
import asyncio

def test_set_speed_limit():
    mock_router = MagicMock()
    assert set_speed_limit(mock_router, "AA:BB:CC:DD:EE:FF", rx_kbps=5000, tx_kbps=2000) is True
    mock_router.rci.assert_called_once()

    mock_router.reset_mock()
    assert set_speed_limit(mock_router, "aa:bb:cc:dd:ee:ff", rx_kbps=0, tx_kbps=0) is True
    call_arg = mock_router.rci.call_args[0][0]
    assert call_arg[0]["ip"]["hotspot"]["host"]["shape"] == {"no" : True}

def test_async_set_speed_limit():
    async def run():
        mock_router = AsyncMock()
        assert await set_speed_limit(mock_router, "11:22:33:44:55:66", rx_kbps=1000) is True
        mock_router.rci.assert_called_once()
    asyncio.run(run())

def test_set_client_access():
    mock_router = MagicMock()
    assert set_client_access(mock_router, "AA:BB:CC:DD:EE:FF", permit=False) is True
    call_arg = mock_router.rci.call_args[0][0]
    assert call_arg[0]["ip"]["hotspot"]["host"]["permit"] is False

    mock_router.reset_mock()
    assert set_client_access(mock_router, "AA:BB:CC:DD:EE:FF", permit=True) is True
    call_arg = mock_router.rci.call_args[0][0]
    assert call_arg[0]["ip"]["hotspot"]["host"]["permit"] is True

def test_async_set_client_access():
    async def run():
        mock_router = AsyncMock()
        assert await set_client_access(mock_router, "11:22:33:44:55:66", permit=False) is True
        mock_router.rci.assert_called_once()
    asyncio.run(run())

def test_set_dhcp_binding():
    mock_router = MagicMock()
    assert set_dhcp_binding(mock_router, "AA:BB:CC:DD:EE:FF", "192.168.1.100", name="MyPC") is True
    call_arg = mock_router.rci.call_args[0][0]
    assert call_arg[0]["ip"]["dhcp"]["host"] == {
        "mac"  : "aa:bb:cc:dd:ee:ff",
        "ip"   : "192.168.1.100",
        "name" : "MyPC"
    }

def test_async_set_dhcp_binding():
    async def run():
        mock_router = AsyncMock()
        assert await set_dhcp_binding(mock_router, "11:22:33:44:55:66", "192.168.1.50") is True
        mock_router.rci.assert_called_once()
    asyncio.run(run())

def test_find_client():
    hosts_data = {
        "host" : [
            {"mac" : "aa:bb:cc:dd:ee:ff", "ip" : "192.168.1.50", "name" : "Home-Laptop"},
            {"mac" : "11:22:33:44:55:66", "ip" : "192.168.1.60", "hostname" : "Pixel-Phone"}
        ]
    }
    assert find_client(hosts_data, "192.168.1.50")["name"] == "Home-Laptop"
    assert find_client(hosts_data, "AA:BB:CC:DD:EE:FF")["ip"] == "192.168.1.50"
    assert find_client(hosts_data, "pixel-phone")["mac"] == "11:22:33:44:55:66"
    assert find_client(hosts_data, "unknown-device") is None
