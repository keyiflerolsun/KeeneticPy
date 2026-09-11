# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from httpx           import AsyncClient, Response, MockTransport
from KeeneticPy.Libs import BGPTools, domain2ip, asn2cidr, ip2asname
import asyncio, pytest

def test_bgptools_class_bindings():
    assert BGPTools.cidr2mask("10.0.0.0/8") == "255.0.0.0"
    assert callable(BGPTools.domain2ip)
    assert callable(BGPTools.asn2cidr)
    assert callable(BGPTools.ip2asname)

def test_asn2cidr_invalid():
    assert asn2cidr("INVALID_ASN") == {}
    assert asn2cidr("") == {}

def test_async_asn2cidr_invalid():
    async def run():
        res = await asn2cidr("NOT_AN_ASN")
        assert res == {}
    asyncio.run(run())

def test_async_domain2ip_mock():
    def mock_handler(request):
        if "dns-query" in str(request.url):
            return Response(200, json={
                "Answer" : [
                    {"name" : "test.local", "type" : 1, "data" : "192.168.1.10"},
                    {"name" : "test.local", "type" : 1, "data" : "192.168.1.11"}
                ]
            })
        return Response(404)

    async def run():
        async with AsyncClient(transport=MockTransport(mock_handler)) as client:
            res = await domain2ip("test.local", client=client)
            assert res["domain"] == "test.local"
            assert "192.168.1.10" in res["ipler"]
            assert "192.168.1.11" in res["ipler"]
            assert res["subnetler"] is not None

    asyncio.run(run())

def test_async_asn2cidr_mock():
    def mock_handler(request):
        url = str(request.url)
        if "as-overview" in url:
            return Response(200, json={"data" : {"holder" : "MOCK-CORP"}})
        if "announced-prefixes" in url:
            return Response(200, json={"data" : {"prefixes" : [{"prefix" : "198.51.100.0/24"}]}})
        return Response(404)

    async def run():
        async with AsyncClient(transport=MockTransport(mock_handler)) as client:
            res = await asn2cidr(64496, client=client)
            assert res["company"] == "MOCK-CORP"
            assert "198.51.100.0/24" in res["prefixes"]

    asyncio.run(run())

def test_ip2asname_mock():
    assert ip2asname("256.256.256.256") == ""

@pytest.mark.integration
def test_domain2ip_live():
    try:
        res = domain2ip("one.one.one.one")
        assert res["domain"] == "one.one.one.one"
        if not res.get("ipler"):
            pytest.skip("DoH servisi yanıt vermedi")
        assert any(ip in ["1.1.1.1", "1.0.0.1"] for ip in res["ipler"])
    except Exception as err:
        pytest.skip(f"Canlı DoH testi atlandı: {err}")

@pytest.mark.integration
def test_asn2cidr_live():
    try:
        data = asn2cidr(13335)
        if not data.get("prefixes"):
            pytest.skip("RIPE Stat servisi yanıt vermedi")
        assert "CLOUDFLARE" in data.get("company", "").upper()
        assert len(data.get("prefixes", [])) > 0
    except Exception as err:
        pytest.skip(f"Canlı ASN testi atlandı: {err}")
