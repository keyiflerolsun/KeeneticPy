# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from httpx                     import AsyncClient, Response, MockTransport
from unittest.mock             import MagicMock, AsyncMock
from KeeneticPy.Libs.RouteSync import parse_route_entries, fetch_route_text, sync_static_routes
import asyncio

def test_parse_route_entries():
    text = """
    # Comment line
    1.1.1.0/24 Cloudflare DNS
    10.0.0.1 Single Host
    // Another comment
    1.1.1.0/24 Duplicate Ignored
    invalid.ip.string
    8.8.8.8 ; Google DNS
    """
    entries = parse_route_entries(text)
    assert len(entries) == 3

    assert entries[0]["network"] == "1.1.1.0"
    assert entries[0]["mask"] == "255.255.255.0"
    assert entries[0]["cidr"] == "1.1.1.0/24"
    assert entries[0]["comment"] == "Cloudflare DNS"

    assert entries[1]["host"] == "10.0.0.1"
    assert entries[1]["cidr"] == "10.0.0.1/32"

    assert entries[2]["host"] == "8.8.8.8"

def test_fetch_route_text_local(tmp_path):
    file_path = tmp_path / "routes.txt"
    file_path.write_text("1.2.3.4/32 Test", encoding="utf-8")
    content = fetch_route_text(str(file_path))
    assert "1.2.3.4/32" in content

def test_fetch_route_text_async_mock():
    def handler(request):
        return Response(200, text="5.5.5.0/24 Cloud")

    async def run():
        async with AsyncClient(transport=MockTransport(handler)) as client:
            content = await fetch_route_text("https://example.com/list.txt", client=client)
            assert "5.5.5.0/24" in content
    asyncio.run(run())

def test_sync_static_routes():
    mock_router                                = MagicMock()
    mock_router.get_static_routes.return_value = [
        {"network" : "10.0.0.0", "mask" : "255.0.0.0", "comment" : "[AutoSync] OldNet", "interface" : "WG0"},
        {"host"    : "1.1.1.1", "comment" : "[AutoSync] Stay", "interface" : "WG0"},
        {"host"    : "9.9.9.9", "comment" : "ManualRoute", "interface" : "ISP"}
    ]
    mock_router.add_static_route.return_value = True
    mock_router.del_static_route.return_value = True

    new_entries = [
        {"host" : "1.1.1.1", "comment" : "Stay", "cidr" : "1.1.1.1/32"},
        {"network" : "192.168.10.0", "mask" : "255.255.255.0", "comment" : "NewNet", "cidr" : "192.168.10.0/24"}
    ]

    res = sync_static_routes(mock_router, new_entries, interface="WG0", tag="AutoSync")
    assert "192.168.10.0/24" in res["added"]
    assert len(res["removed"]) == 1
    assert res["total"] == 2

    mock_router.add_static_route.assert_called_once()
    mock_router.del_static_route.assert_called_once_with(
        network   = "10.0.0.0",
        mask      = "255.0.0.0",
        comment   = "[AutoSync] OldNet",
        interface = "WG0"
    )

def test_async_sync_static_routes():
    async def run():
        mock_router                                = AsyncMock()
        mock_router.get_static_routes.return_value = []
        mock_router.add_static_route.return_value  = True

        new_entries = [{"host" : "4.4.4.4", "cidr" : "4.4.4.4/32"}]
        res         = await sync_static_routes(mock_router, new_entries, tag="TestTag")

        assert "4.4.4.4/32" in res["added"]
        assert res["total"] == 1
        mock_router.add_static_route.assert_called_once()

    asyncio.run(run())
