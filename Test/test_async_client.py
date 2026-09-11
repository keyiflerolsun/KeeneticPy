# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from httpx           import Response, MockTransport, AsyncClient
from KeeneticPy.Core import AsyncKeenetic, KeeneticConnectionError, KeeneticAuthError
import asyncio
import json
import pytest

def make_router_handler():
    def handler(request):
        path = request.url.path

        if path == "/auth":
            if request.method == "GET":
                return Response(
                    401,
                    headers = {
                        "X-NDM-Realm"     : "Keenetic",
                        "X-NDM-Challenge" : "0123456789abcdef0123456789abcdef"
                    }
                )
            if request.method == "POST":
                data = json.loads(request.content)
                if data.get("login") == "admin":
                    return Response(200, json={"status" : "authorized"})
                return Response(401, json={"status" : "unauthorized"})

        if "/rci/show/system" in path:
            return Response(200, json={"uptime" : 7200, "cpuload" : 8})

        if "/rci/show/version" in path:
            return Response(200, json={"model" : "KN-1011", "release" : "4.02", "device" : "Keenetic-Giga"})

        if "/rci/show/interface" in path:
            return Response(200, json={
                "Wireguard0" : {"interface-name" : "WG0", "type" : "Wireguard", "description" : "VPN"}
            })

        if "/rci/show/ip/hotspot" in path:
            return Response(200, json={"host" : []})

        if "/rci/" in path and request.method == "POST":
            return Response(200, json=[{"status" : [{"status" : "message", "message" : "done"}]}])

        if "/ci/firmware" in path or "/ci/startup-config" in path:
            return Response(200, content=b"async-data")

        return Response(404)

    return handler

def make_async_client():
    handler       = make_router_handler()
    client        = AsyncKeenetic(user="admin", password="password", panel="http://192.168.1.1")
    client.oturum = AsyncClient(transport=MockTransport(handler))
    return client

def test_async_client_connection_failure():
    async def run():
        with pytest.raises(KeeneticConnectionError):
            client = AsyncKeenetic(user="admin", password="password", panel="http://127.0.0.1:59999", timeout=0.5)
            await client.authenticate()
    asyncio.run(run())

def test_async_client_auth_success():
    async def run():
        client = make_async_client()
        res    = await client.authenticate()
        assert res is True
        assert client._yetkili is True
        await client.close()
    asyncio.run(run())

def test_async_client_auth_invalid():
    def fail_handler(request):
        if request.url.path == "/auth":
            if request.method == "GET":
                return Response(401, headers={"X-NDM-Realm" : "K", "X-NDM-Challenge" : "123"})
            return Response(401)
        return Response(404)

    async def run():
        client        = AsyncKeenetic(user="wrong", password="wrong", panel="http://192.168.1.1")
        client.oturum = AsyncClient(transport=MockTransport(fail_handler))
        with pytest.raises(KeeneticAuthError):
            await client.authenticate()
        await client.close()
    asyncio.run(run())

def test_async_client_queries():
    async def run():
        client = make_async_client()
        sys    = await client.system()
        assert sys.get("uptime") == 7200

        ver = await client.version()
        assert ver.get("model") == "KN-1011"

        ifaces = await client.get_interface_names()
        assert len(ifaces) == 1
        assert ifaces[0]["description"] == "VPN"

        hosts = await client.hosts()
        assert hosts.get("host") == []
        await client.close()
    asyncio.run(run())

def test_async_client_routes_and_commands():
    async def run():
        client = make_async_client()
        assert await client.add_static_route(comment="AsyncRoute", host="8.8.8.8", interface="Wireguard0") is True
        assert await client.del_static_route(comment="AsyncRoute", host="8.8.8.8", interface="Wireguard0") is True
        assert await client.reboot() is True
        assert await client.wol("00:11:22:33:44:55") is True
        assert await client.dsl_reset() is True
        await client.close()
    asyncio.run(run())

def test_async_client_context_manager():
    async def run():
        client = make_async_client()
        async with client as r:
            assert r._yetkili is True
    asyncio.run(run())

def test_async_client_backup(tmp_path):
    async def run():
        client = make_async_client()
        path   = await client.backup(max_backups=2, target_dir=str(tmp_path))
        assert path.endswith(".zip")
        await client.close()
    asyncio.run(run())
