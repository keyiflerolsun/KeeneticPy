# KeeneticPy 📡

<div align="center">

**[ English ](README.md)** • **[ Türkçe ](README.tr.md)** • **[ Русский ](README.ru.md)** • **[ Deutsch ](README.de.md)**

[![Size](https://img.shields.io/github/repo-size/keyiflerolsun/KeeneticPy?logo=git&logoColor=white&label=Size)](#)
[![Views](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/keyiflerolsun/KeeneticPy&title=Views)](#)
<a href="https://KekikAkademi.org/Kahve" target="_blank"><img src="https://img.shields.io/badge/☕️-Buy%20Coffee-ffdd00" title="☕️ Buy Me a Coffee" style="padding-left:5px;"></a>

[![PyPI](https://img.shields.io/pypi/v/KeeneticPy?logo=pypi&logoColor=white&label=PyPI)](https://pypi.org/project/KeeneticPy)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/KeeneticPy?logo=pypi&logoColor=white&label=Downloads)](https://pypi.org/project/KeeneticPy)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/KeeneticPy?logo=pypi&logoColor=white&label=Wheel)](https://pypi.org/project/KeeneticPy)
[![Python Version](https://img.shields.io/pypi/pyversions/KeeneticPy?logo=python&logoColor=white&label=Python)](#)
[![License](https://img.shields.io/pypi/l/KeeneticPy?logo=gnu&logoColor=white&label=License)](#)
[![Status](https://img.shields.io/pypi/status/KeeneticPy?logo=windowsterminal&logoColor=white&label=Status)](#)
[![PyPI Publish](https://github.com/keyiflerolsun/KeeneticPy/actions/workflows/PyPI.yml/badge.svg)](https://github.com/keyiflerolsun/KeeneticPy/actions/workflows/PyPI.yml)

</div>

**Modern, Async/Sync Python Library & CLI for Keenetic Routers (KeeneticOS RCI)**

KeeneticPy is an advanced Python package and CLI tool for Keenetic routers powered by KeeneticOS. It provides **WireGuard / VPN policy-based routing (Domain & ASN routing)**, **automated CIDR list synchronization**, **4G/LTE modem & SMS automation**, **client bandwidth throttling**, **Prometheus metrics export**, and system monitoring.

---

## ✨ Features

* ⚡ **Sync & Async Support**: Full support for both `Keenetic` (synchronous) and `AsyncKeenetic` (`async with`), natively compatible with **Home Assistant** and **FastAPI**.
* 🛡️ **Zero Heavy Dependencies**: Lightweight and fast architecture built exclusively on `httpx` and `rich`.
* 🌐 **BGP & Policy-Based Routing (PBR)**: Route domains via Cloudflare DoH or entire ASN prefixes (via RIPE Stat API) to WireGuard / VPN tunnels in a single call.
* 🔄 **Bulk Route Sync**: Synchronize static routes directly from URLs or local text files with automatic pruning of obsolete entries (`route sync`).
* 📶 **4G/LTE Modem & SMS Management**: Monitor cellular signal quality (RSRP, RSRQ, SINR, Band, Carrier), read incoming SMS, send SMS messages, and execute USSD codes.
* 👥 **Client & Bandwidth Controls**: Throttle download/upload speeds per MAC, toggle internet access (block/unblock), and configure static DHCP leases.
* 📶 **DSL & Mesh Diagnostics**: Parse raw VDSL2/ADSL driver stats into readable SNR/attenuation/error tables (`dsl stats`, `dsl reset`), and list Mesh Wi-Fi System (MWS) extender nodes with CPU/RAM/backhaul info (`mesh`).
* 🔄 **Live Watch Mode**: Add `--watch` to `hosts`, `mesh`, or `dsl stats` for an auto-refreshing terminal dashboard.
* 📊 **Built-in Prometheus Exporter**: Serve real-time system, network traffic, and client metrics for Prometheus and Grafana dashboards (`keenetic exporter`).
* 💻 **Feature-Rich CLI**: Manage your router entirely from the terminal.
* 💾 **Smart Backup Rotation**: Automatically download and rotate timestamped zip archives containing firmware and `startup-config.txt`.

---

## 🚀 Installation

```bash
# Using pip
pip install -U KeeneticPy

# Using uv
uv add KeeneticPy
```

---

## 💻 CLI Usage (Terminal)

The `keenetic` CLI command is available immediately after installation:

```bash
# Display router status, CPU/RAM load, and WAN IPs
keenetic --password "your_password" info

# List connected hotspot clients and real-time traffic (Rx/Tx)
keenetic --password "your_password" hosts

# Show Mesh Wi-Fi System extender nodes (or reboot one by its CID)
keenetic --password "your_password" mesh
keenetic --password "your_password" mesh reboot <cid>

# DSL line diagnostics (SNR, attenuation, error counters), or reset the link
keenetic --password "your_password" dsl stats
keenetic --password "your_password" dsl reset

# Live-refreshing dashboard (works with hosts / mesh / dsl stats)
keenetic --password "your_password" hosts --watch --interval 5

# Route a domain to WireGuard VPN
keenetic --password "your_password" route add-domain discord.com --interface Wireguard0

# Route Cloudflare ASN (13335) IP prefixes to WireGuard
keenetic --password "your_password" route add-asn 13335 --interface Wireguard0

# Synchronize routes from remote URL or local file (auto-prunes stale routes)
keenetic --password "your_password" route sync https://antifilter.download/list/allyouneed.lst --interface Wireguard0

# Set device bandwidth limit (5 Mbps down, 1 Mbps up)
keenetic --password "your_password" client limit AA:BB:CC:DD:EE:FF --rx 5000 --tx 1000

# Block / unblock device internet access
keenetic --password "your_password" client block AA:BB:CC:DD:EE:FF
keenetic --password "your_password" client unblock AA:BB:CC:DD:EE:FF

# Assign static DHCP lease
keenetic --password "your_password" client bind AA:BB:CC:DD:EE:FF 192.168.1.100 -n "Desktop-PC"

# 4G/LTE modem signal diagnostics & SMS
keenetic --password "your_password" modem status
keenetic --password "your_password" modem sms-list
keenetic --password "your_password" modem sms-send +1234567890 "Server alert"
keenetic --password "your_password" modem ussd "*100#"

# Run standalone Prometheus metrics exporter on port 9100
keenetic --password "your_password" exporter --port 9100

# Download router backup (firmware + config)
keenetic --password "your_password" backup --keep 5

# Reboot router remotely
keenetic --password "your_password" reboot
```

> **Tip:** Avoid passing credentials in CLI arguments by setting environment variables:
> ```bash
> export KEENETIC_USER="admin"
> export KEENETIC_PASSWORD="your_router_password"
> export KEENETIC_PANEL="http://192.168.1.1"
> ```

---

## 📝 Python Usage

### 1. Synchronous Client (`Keenetic`)

```python
from KeeneticPy import Keenetic, set_speed_limit, set_client_access, get_modem_info, send_sms

with Keenetic(user="admin", password="password", panel="http://192.168.1.1") as router:
    # System details
    print("Version:", router.version())
    print("WAN IP:", router.global_ip())

    # Add domain route to WireGuard
    router.add_route_with_domain("discord.com", interface="Wireguard0")

    # Set 10 Mbps bandwidth limit for a phone
    set_speed_limit(router, "aa:bb:cc:dd:ee:ff", rx_kbps=10000, tx_kbps=5000)

    # Check 4G/LTE signal strength
    modem = get_modem_info(router)
    print("Cellular Operator:", modem.get("operator"))
    print("RSRP Signal:", modem.get("rsrp"))

    # Send SMS notification
    send_sms(router, "+1234567890", "Router backup completed successfully.")

    # Create backup
    router.backup(max_backups=3)
```

---

### 2. Asynchronous Client (`AsyncKeenetic` - Home Assistant / FastAPI)

```python
import asyncio
from KeeneticPy import AsyncKeenetic, sync_static_routes, parse_route_entries, fetch_route_text

async def main():
    async with AsyncKeenetic(user="admin", password="password", panel="http://192.168.1.1") as router:
        hosts = await router.hosts()
        print("Connected clients count:", len(hosts.get("host", [])))

        # Sync remote IP list to Wireguard
        raw_routes = fetch_route_text("https://example.com/routes.txt")
        entries = parse_route_entries(raw_routes)
        result = await sync_static_routes(router, entries, interface="Wireguard0")
        print("Sync result:", result)

asyncio.run(main())
```

---

### 3. BGP & DNS Lookup Utilities (`BGPTools`)

```python
from KeeneticPy import domain2ip, asn2cidr, cidr2mask, mask2cidr

# Resolve domain via Cloudflare DoH and collapse to CIDR subnets
result = domain2ip("github.com")
print("IPs:", result["ipler"])
print("Subnets:", result["subnetler"])

# Fetch IPv4 announced prefixes from official RIPE Stat API
cloudflare = asn2cidr(13335)
print("Company:", cloudflare["company"])
print("Prefixes count:", len(cloudflare["prefixes"]))

# Subnet conversions
print(cidr2mask("192.168.1.0/24"))  # 255.255.255.0
print(mask2cidr("255.255.255.0"))    # 24
```

---

## 💸 Sponsor & Support

**[☕️ Buy Me a Coffee](https://KekikAkademi.org/Kahve)**

## 🌐 Copyright and License

* *Copyright (C) 2023 - 2026 by* [keyiflerolsun](https://github.com/keyiflerolsun) ❤️️
* Licensed under the terms of the [GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007](https://github.com/keyiflerolsun/KeeneticPy/blob/main/LICENSE).

## ♻️ Contact

*Feel free to reach out via **Telegram**;* [@keyiflerolsun](https://t.me/KekikKahve)

> *Written for* **[@KekikAkademi](https://t.me/KekikAkademi)**
