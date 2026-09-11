# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from httpx           import Response, MockTransport
from KeeneticPy.Core import Keenetic, KeeneticError, KeeneticAuthError, KeeneticRCIError, KeeneticConnectionError
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
                        "X-NDM-Challenge" : "fedcba9876543210fedcba9876543210"
                    }
                )
            if request.method == "POST":
                data = json.loads(request.content)
                if data.get("login") == "admin":
                    return Response(200, json={"status" : "authorized"})
                return Response(401, json={"status" : "unauthorized"})

        if "/rci/show/system" in path:
            return Response(200, json={"uptime" : 3600, "cpuload" : 12})

        if "/rci/show/version" in path:
            return Response(200, json={"model" : "KN-1810", "release" : "4.01", "device" : "Keenetic-Ultra"})

        if "/rci/show/interface" in path:
            return Response(200, json={
                "GigabitEthernet0/0" : {"interface-name" : "GE0", "type" : "Ethernet", "description" : "LAN 1"},
                "Wireguard0"         : {"interface-name" : "WG0", "type" : "Wireguard", "description" : "VPN Tunnel"}
            })

        if "/rci/show/ip/hotspot" in path:
            return Response(200, json={
                "host" : [
                    {"name" : "Phone", "ip" : "192.168.1.50", "mac" : "aa:bb:cc:dd:ee:ff", "active" : True, "rxbytes" : 1000, "txbytes" : 2000}
                ]
            })

        if "/rci/" in path and request.method == "POST":
            return Response(200, json=[{"status" : [{"status" : "message", "message" : "done"}]}])

        if "/ci/firmware" in path or "/ci/startup-config" in path:
            return Response(200, content=b"fake-content")

        return Response(404)

    return handler

def make_mock_client():
    handler = make_router_handler()
    return Keenetic(user="admin", password="secret", panel="http://192.168.1.1", transport=MockTransport(handler))

def test_client_connection_failure():
    with pytest.raises(KeeneticConnectionError):
        Keenetic(user="admin", password="password", panel="http://127.0.0.1:59999", timeout=0.5)

def test_client_auth_success():
    router = make_mock_client()
    assert router._yetki is True
    router.close()

def test_client_auth_invalid_credentials():
    def fail_handler(request):
        if request.url.path == "/auth":
            if request.method == "GET":
                return Response(401, headers={"X-NDM-Realm" : "K", "X-NDM-Challenge" : "123"})
            return Response(401)
        return Response(404)

    with pytest.raises(KeeneticAuthError):
        Keenetic(user="wrong", password="wrong", panel="http://192.168.1.1", transport=MockTransport(fail_handler))

def test_client_system_queries():
    router = make_mock_client()
    sys    = router.system()
    assert sys.get("uptime") == 3600

    ver = router.version()
    assert ver.get("model") == "KN-1810"

    ifaces = router.get_interface_names()
    assert len(ifaces) == 2
    assert ifaces[0]["description"] == "LAN 1"

    hosts = router.hosts()
    assert len(hosts["host"]) == 1

def test_client_route_management():
    router = make_mock_client()
    assert router.add_static_route(comment="DNS", host="1.1.1.1", interface="Wireguard0") is True
    assert router.del_static_route(comment="DNS", host="1.1.1.1", interface="Wireguard0") is True

def test_client_dsl_and_reboot():
    router = make_mock_client()
    assert router.dsl_reset() is True
    assert router.reboot() is True
    assert router.wol("aa:bb:cc:dd:ee:ff") is True

def test_client_backup(tmp_path):
    router = make_mock_client()
    path   = router.backup(max_backups=2, target_dir=str(tmp_path))
    assert path.endswith(".zip")

def test_client_context_manager():
    with make_mock_client() as router:
        assert router._yetki is True

def test_client_rci_error():
    def err_handler(request):
        if request.url.path == "/auth":
            if request.method == "GET":
                return Response(401, headers={"X-NDM-Realm" : "K", "X-NDM-Challenge" : "123"})
            return Response(200, json={"status" : "authorized"})
        if "/rci/" in request.url.path:
            return Response(500, text="Internal Error")
        return Response(404)

    with Keenetic(user="admin", password="secret", panel="http://192.168.1.1", transport=MockTransport(err_handler)) as router:
        with pytest.raises(KeeneticRCIError):
            router.rci({"show" : {"system" : {}}})

def test_exceptions_inheritance():
    assert issubclass(KeeneticAuthError, KeeneticError)
    assert issubclass(KeeneticRCIError, KeeneticError)
    assert issubclass(KeeneticConnectionError, KeeneticError)
