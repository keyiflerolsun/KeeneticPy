# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from KeeneticPy.Libs.Helpers import slugify, cidr2mask, mask2cidr, format_bytes, build_route_payload, extract_wan_ips, save_backup_archive, parse_dsl_stats, parse_mesh_nodes, describe_host_link
from zipfile                 import ZipFile
import os
import pytest

def test_slugify_basic():
    assert slugify("Keenetic Hero 4G+") == "keenetic-hero-4g"
    assert slugify("Ultra KN-1810") == "ultra-kn-1810"
    assert slugify("  Extra-DSL  ") == "extra-dsl"
    assert slugify("Multiple---Dashes___Here") == "multiple-dashes-here"

def test_slugify_turkish():
    assert slugify("Türkçe Test Başlığı") == "turkce-test-basligi"
    assert slugify("Şampiyonlar Ligi Çeyrek Final") == "sampiyonlar-ligi-ceyrek-final"
    assert slugify("Ömer Faruk Işık") == "omer-faruk-isik"

def test_slugify_unicode_flag():
    assert slugify("Türkçe", allow_unicode=True) == "türkçe"
    assert slugify("Geliştirici", allow_unicode=True) == "geliştirici"

def test_cidr2mask_valid():
    assert cidr2mask("192.168.1.0/24") == "255.255.255.0"
    assert cidr2mask("10.0.0.0/8") == "255.0.0.0"
    assert cidr2mask("172.16.0.0/16") == "255.255.0.0"
    assert cidr2mask("1.1.1.1/32") == "255.255.255.255"
    assert cidr2mask("10.10.10.0/28") == "255.255.255.240"
    assert cidr2mask("0.0.0.0/0") == "0.0.0.0"

def test_mask2cidr_valid():
    assert mask2cidr("255.255.255.0") == 24
    assert mask2cidr("255.0.0.0") == 8
    assert mask2cidr("255.255.0.0") == 16
    assert mask2cidr("255.255.255.255") == 32
    assert mask2cidr("255.255.255.240") == 28
    assert mask2cidr("0.0.0.0") == 0

def test_format_bytes():
    assert format_bytes(0) == "0 B"
    assert format_bytes(-10) == "0 B"
    assert format_bytes(512) == "512.0 B"
    assert format_bytes(1024) == "1.0 KB"
    assert format_bytes(1024 * 1024) == "1.0 MB"
    assert format_bytes(1024 * 1024 * 1024) == "1.0 GB"
    assert format_bytes(1024 * 1024 * 1024 * 1024 * 2.5) == "2.5 TB"

def test_build_route_payload_host():
    payload = build_route_payload(comment="Cloudflare", host="1.1.1.1", interface="Wireguard0")
    assert payload == {
        "interface" : "Wireguard0",
        "comment"   : "Cloudflare",
        "host"      : "1.1.1.1"
    }

def test_build_route_payload_network():
    payload = build_route_payload(comment="Subnet", network="10.0.0.0", mask="255.0.0.0", interface="Wireguard1", no=True)
    assert payload == {
        "interface" : "Wireguard1",
        "comment"   : "Subnet",
        "network"   : "10.0.0.0",
        "mask"      : "255.0.0.0",
        "no"        : True
    }

def test_build_route_payload_validation():
    with pytest.raises(ValueError, match="Please provide 'host' or"):
        build_route_payload(comment="Missing destination")

    with pytest.raises(ValueError):
        build_route_payload(network="10.0.0.0")

def test_extract_wan_ips():
    sample_pppoe = {
        "show"      : {
            "interface" : {"PPPoE0" : {"address" : "85.105.1.2"}},
            "ipv6"      : {"addresses" : {"address" : [{"address" : "2001:db8::1"}]}}
        }
    }
    extracted = extract_wan_ips(sample_pppoe)
    assert extracted["ipv4"] == "85.105.1.2"
    assert extracted["ipv6"] == "2001:db8::1"

    sample_isp = {
        "show"      : {
            "interface" : {"ISP" : {"address" : "192.168.2.100"}}
        }
    }
    assert extract_wan_ips(sample_isp) == {"ipv4" : "192.168.2.100", "ipv6" : None}
    assert extract_wan_ips({}) == {"ipv4" : None, "ipv6" : None}

def test_save_backup_archive(tmp_path):
    target_dir = str(tmp_path)
    zip_path   = os.path.join(target_dir, "test-router_v1_01-01-2026.zip")

    save_backup_archive(
        zip_path    = zip_path,
        fw_bytes    = b"mock-firmware-data",
        cfg_bytes   = b"mock-config-data",
        max_backups = 2,
        target_dir  = target_dir
    )

    assert os.path.exists(zip_path)
    with ZipFile(zip_path, "r") as zf:
        assert zf.namelist() == ["firmware.bin", "startup-config.txt"]
        assert zf.read("firmware.bin") == b"mock-firmware-data"
        assert zf.read("startup-config.txt") == b"mock-config-data"

    for i in range(3):
        path = os.path.join(target_dir, f"test-router_v1_0{i+2}-01-2026.zip")
        save_backup_archive(
            zip_path    = path,
            fw_bytes    = b"data",
            max_backups = 2,
            target_dir  = target_dir
        )

    remaining = [f for f in os.listdir(target_dir) if f.endswith(".zip")]
    assert len(remaining) == 2

def test_parse_dsl_stats():
    raw = {
        "parse"   : {
            "message" : [
                "DSL link status:               showtime            ",
                "Uptime:                        3 day, 16:26:08     ",
                "Mode:                          ITU G.993.2 (VDSL2) ",
                "",
                "Fast (Kbps):                   76795               15359         ",
                "FEC errors fast:               2903088693          67                  ",
                "",
                "SNR margin (dB)",
                "Band 0:                        3.9                 18.1                ",
                "Band 3:                        N/A                 N/A                 ",
                "",
                "Carrier load (bits per tone)",
                "tone   0-31 : 00 00 00 03 45 66  66 77 77 77 66 66 55 54 43 21",
            ],
            "prompt" : "(config)"
        }
    }
    parsed = parse_dsl_stats(raw)

    assert parsed["general"] == {
        "DSL link status" : "showtime",
        "Uptime"          : "3 day, 16:26:08",
        "Mode"            : "ITU G.993.2 (VDSL2)"
    }
    assert parsed["pairs"] == {
        "Fast (Kbps)"              : ("76795", "15359"),
        "FEC errors fast"          : ("2903088693", "67"),
        "SNR margin (dB) - Band 0" : ("3.9", "18.1"),
        "SNR margin (dB) - Band 3" : ("N/A", "N/A")
    }

def test_parse_dsl_stats_empty():
    assert parse_dsl_stats({}) == {"general" : {}, "pairs" : {}}
    assert parse_dsl_stats({"parse" : {"message" : []}}) == {"general" : {}, "pairs" : {}}

def test_parse_mesh_nodes():
    members = [
        {
            "cid"                : "a4a2506e-4dae-11ed-9396-3be15a4fcdf3",
            "model"              : "Sprinter (KN-3710)",
            "mac"                : "50:ff:20:90:63:64",
            "known-host"         : "Üst - Sprinter (KN-3710)",
            "ip"                 : "192.168.1.2",
            "mode"               : "extender",
            "fw"                 : "5.1.4",
            "internet-available" : True,
            "associations"       : 4,
            "system"             : {"cpuload" : 2, "memory" : "95804/262144", "uptime" : "1184489"},
            "rci"                : {"errors" : 0},
            "backhaul"           : {"speed" : "1000", "duplex" : "full"}
        },
        {
            "cid"                : "b5b3617f-5eaf-22fe-a4a7-4cf26b5edea4",
            "model"              : "Hero DSL (KN-2410)",
            "mac"                : "50:ff:20:75:58:40",
            "known-host"         : None,
            "ip"                 : "192.168.1.3",
            "mode"               : "extender",
            "fw"                 : "5.1.4",
            "internet-available" : False,
            "associations"       : 0,
            "system"             : {"cpuload" : 1, "memory" : "76020/262144", "uptime" : "500"},
            "rci"                : {"errors" : 3},
            "backhaul"           : {}
        }
    ]
    nodes = parse_mesh_nodes(members)
    assert len(nodes) == 2

    connected = nodes[0]
    assert connected["name"] == "Üst - Sprinter (KN-3710)"
    assert connected["connected"] is True
    assert connected["memory_pct"] == 36.5
    assert connected["backhaul"] == "1000 Mbps (full)"

    disconnected = nodes[1]
    assert disconnected["name"] == "Hero DSL (KN-2410)"
    assert disconnected["connected"] is False
    assert disconnected["backhaul"] is None

def test_parse_mesh_nodes_empty():
    assert parse_mesh_nodes([]) == []

def test_describe_host_link():
    assert describe_host_link(None) == "-"
    assert describe_host_link({}) == "-"
    assert describe_host_link({"rssi" : -63, "ap" : "WifiMaster1/AccessPoint1"}) == "📶 -63 dBm"
    assert describe_host_link({"port" : "3", "speed" : 1000, "duplex" : True}) == "🔌 Port 3"
