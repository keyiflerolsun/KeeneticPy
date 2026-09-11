# KeeneticPy 📡

<div align="center">

**[ English ](README.md)** • **[ Türkçe ](README.tr.md)** • **[ Русский ](README.ru.md)** • **[ Deutsch ](README.de.md)**

[![Größe](https://img.shields.io/github/repo-size/keyiflerolsun/KeeneticPy?logo=git&logoColor=white&label=Größe)](#)
[![Aufrufe](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/keyiflerolsun/KeeneticPy&title=Aufrufe)](#)
<a href="https://KekikAkademi.org/Kahve" target="_blank"><img src="https://img.shields.io/badge/☕️-Kaffee%20kaufen-ffdd00" title="☕️ Kauf mir einen Kaffee" style="padding-left:5px;"></a>

[![PyPI](https://img.shields.io/pypi/v/KeeneticPy?logo=pypi&logoColor=white&label=PyPI)](https://pypi.org/project/KeeneticPy)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/KeeneticPy?logo=pypi&logoColor=white&label=Downloads)](https://pypi.org/project/KeeneticPy)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/KeeneticPy?logo=pypi&logoColor=white&label=Wheel)](https://pypi.org/project/KeeneticPy)
[![Python Version](https://img.shields.io/pypi/pyversions/KeeneticPy?logo=python&logoColor=white&label=Python)](#)
[![Lizenz](https://img.shields.io/pypi/l/KeeneticPy?logo=gnu&logoColor=white&label=Lizenz)](#)
[![Status](https://img.shields.io/pypi/status/KeeneticPy?logo=windowsterminal&logoColor=white&label=Status)](#)
[![PyPI Publish](https://github.com/keyiflerolsun/KeeneticPy/actions/workflows/PyPI.yml/badge.svg)](https://github.com/keyiflerolsun/KeeneticPy/actions/workflows/PyPI.yml)

</div>

**Moderne, asynchrone und synchrone Python-Bibliothek und CLI für Keenetic-Router (KeeneticOS RCI)**

KeeneticPy ist ein fortschrittliches Python-Paket und CLI-Tool für KeeneticOS-betriebene Router über die offizielle `RCI`-Schnittstelle (Remote Control Interface). Es ermöglicht **WireGuard / VPN Policy-Based Routing (PBR nach Domains & ASN)**, **automatische CIDR-Routensynchronisation**, **4G/LTE-Modem- und SMS-Automatisierung**, **Bandbreitenbegrenzung für Clients**, **integrierten Prometheus-Metrik-Export** sowie automatische Backup-Rotation.

---

## ✨ Funktionen

* ⚡ **Sync- & Async-Unterstützung**: Nahtlose Unterstützung für `Keenetic` (synchron) und `AsyncKeenetic` (`async with`), ideal für **Home Assistant** und **FastAPI**.
* 🛡️ **Keine schweren Abhängigkeiten**: Schlanke und performante Architektur basierend auf `httpx` und `rich`.
* 🌐 **BGP & Policy-Based Routing (PBR)**: Weiterleitung von Domains (via Cloudflare DoH) oder gesamten ASN-Präfixen (via RIPE Stat API) an WireGuard / VPN-Tunnel mit einem einzigen Befehl.
* 🔄 **Massen-Routensynchronisation**: Synchronisieren statischer Routen aus Web-URLs oder lokalen Dateien mit automatischem Bereinigen veralteter Einträge (`route sync`).
* 📶 **4G/LTE-Modem- & SMS-Verwaltung**: Überwachung von Mobilfunksignalen (RSRP, RSRQ, SINR, Band, Provider), Empfangen und Senden von SMS sowie USSD-Code-Abfragen (z.B. Guthaben `*100#`).
* 👥 **Client-Steuerung & Bandbreiten-Drosselung**: Download-/Upload-Limits pro MAC-Adresse, Internetzugriff sperren/freigeben und statische DHCP-Reservierungen.
* 📶 **DSL- & Mesh-Diagnose**: Rohe VDSL2/ADSL-Treiberstatistik in lesbare SNR-/Dämpfungs-/Fehlertabellen umwandeln (`dsl stats`, `dsl reset`) und Mesh-Wi-Fi-System (MWS) Extender-Knoten mit CPU/RAM/Backhaul anzeigen (`mesh`).
* 🔄 **Live-Watch-Modus**: `--watch` zu `hosts`, `mesh` oder `dsl stats` hinzufügen für ein sich automatisch aktualisierendes Terminal-Dashboard.
* 📊 **Integrierter Prometheus Exporter**: Live-Metriken des Routers und der Clients für Grafana-Dashboards bereitstellen (`keenetic exporter`).
* 💻 **Vollständiges CLI**: Den Router komfortabel direkt aus dem Terminal verwalten.
* 💾 **Smarte Backup-Rotation**: Zeitgestempelte ZIP-Archive von Firmware und `startup-config.txt` herunterladen und rotieren.

---

## 🚀 Installation

```bash
# Mit pip
pip install -U KeeneticPy

# Mit uv
uv add KeeneticPy
```

---

## 💻 CLI-Nutzung (Terminal)

Nach der Installation steht der Befehl `keenetic` im Terminal zur Verfügung:

```bash
# Router-Status, CPU/RAM-Auslastung und WAN-IPs anzeigen
keenetic --password "dein_passwort" info

# Verbundene Hotspot-Clients und Echtzeit-Traffic (Rx/Tx) auflisten
keenetic --password "dein_passwort" hosts

# Mesh-Wi-Fi-System Extender-Knoten anzeigen (oder einen Knoten per CID neustarten)
keenetic --password "dein_passwort" mesh
keenetic --password "dein_passwort" mesh reboot <cid>

# DSL-Leitungsdiagnose (SNR, Dämpfung, Fehlerzähler) oder Leitung zurücksetzen
keenetic --password "dein_passwort" dsl stats
keenetic --password "dein_passwort" dsl reset

# Sich automatisch aktualisierendes Dashboard (funktioniert mit hosts / mesh / dsl stats)
keenetic --password "dein_passwort" hosts --watch --interval 5

# Domain-Traffic über WireGuard-VPN leiten
keenetic --password "dein_passwort" route add-domain discord.com --interface Wireguard0

# Cloudflare ASN (13335) IP-Präfixe über WireGuard leiten
keenetic --password "dein_passwort" route add-asn 13335 --interface Wireguard0

# Routen aus Remote-URL oder lokaler Datei synchronisieren (löscht veraltete Routen automatisch)
keenetic --password "dein_passwort" route sync https://antifilter.download/list/allyouneed.lst --interface Wireguard0

# Bandbreitenlimit für Gerät festlegen (5 Mbit/s Down, 1 Mbit/s Up)
keenetic --password "dein_passwort" client limit AA:BB:CC:DD:EE:FF --rx 5000 --tx 1000

# Internetzugriff für ein Gerät blockieren / freigeben
keenetic --password "dein_passwort" client block AA:BB:CC:DD:EE:FF
keenetic --password "dein_passwort" client unblock AA:BB:CC:DD:EE:FF

# Statische DHCP-Lease zuweisen
keenetic --password "dein_passwort" client bind AA:BB:CC:DD:EE:FF 192.168.1.100 -n "Desktop-PC"

# 4G/LTE-Modem Signaldiagnose & SMS
keenetic --password "dein_passwort" modem status
keenetic --password "dein_passwort" modem sms-list
keenetic --password "dein_passwort" modem sms-send +491701234567 "Server-Benachrichtigung"
keenetic --password "dein_passwort" modem ussd "*100#"

# Eigenständigen Prometheus Exporter auf Port 9100 starten
keenetic --password "dein_passwort" exporter --port 9100

# Router-Backup herunterladen (die letzten 5 behalten)
keenetic --password "dein_passwort" backup --keep 5

# Router aus der Ferne neustarten
keenetic --password "dein_passwort" reboot
```

> **Tipp:** Sie können Zugangsdaten über Umgebungsvariablen definieren, um die Eingabe im Terminal zu vermeiden:
> ```bash
> export KEENETIC_USER="admin"
> export KEENETIC_PASSWORD="dein_passwort"
> export KEENETIC_PANEL="http://192.168.1.1"
> ```

---

## 📝 Python-Verwendung

### 1. Synchroner Client (`Keenetic`)

```python
from KeeneticPy import Keenetic, set_speed_limit, set_client_access, get_modem_info, send_sms

with Keenetic(user="admin", password="password", panel="http://192.168.1.1") as router:
    # Systeminformationen
    print("Version:", router.version())
    print("WAN IP:", router.global_ip())

    # Domain-Route zu WireGuard hinzufügen
    router.add_route_with_domain("discord.com", interface="Wireguard0")

    # 10 Mbit/s Bandbreitenlimit für ein Smartphone setzen
    set_speed_limit(router, "aa:bb:cc:dd:ee:ff", rx_kbps=10000, tx_kbps=5000)

    # 4G/LTE Signalstärke prüfen
    modem = get_modem_info(router)
    print("Mobilfunk-Betreiber:", modem.get("operator"))
    print("RSRP Signal:", modem.get("rsrp"))

    # SMS-Benachrichtigung versenden
    send_sms(router, "+491701234567", "Router-Backup erfolgreich abgeschlossen.")

    # Backup erstellen
    router.backup(max_backups=3)
```

---

### 2. Asynchroner Client (`AsyncKeenetic` — Home Assistant / FastAPI)

```python
import asyncio
from KeeneticPy import AsyncKeenetic, sync_static_routes, parse_route_entries, fetch_route_text

async def main():
    async with AsyncKeenetic(user="admin", password="password", panel="http://192.168.1.1") as router:
        hosts = await router.hosts()
        print("Verbundene Geräte:", len(hosts.get("host", [])))

        # Externe Routenliste abrufen und mit WireGuard synchronisieren
        raw_routes = fetch_route_text("https://example.com/routes.txt")
        entries = parse_route_entries(raw_routes)
        result = await sync_static_routes(router, entries, interface="Wireguard0")
        print("Synchronisationsergebnis:", result)

asyncio.run(main())
```

---

### 3. BGP & DNS Hilfswerkzeuge (`BGPTools`)

```python
from KeeneticPy import domain2ip, asn2cidr, cidr2mask, mask2cidr

# Domain über DoH auflösen und zu CIDR-Subnetzen zusammenfassen
result = domain2ip("github.com")
print("IPs:", result["ipler"])
print("Subnetze:", result["subnetler"])

# IPv4-Präfixe für eine ASN von der offiziellen RIPE Stat API abrufen
cloudflare = asn2cidr(13335)
print("Unternehmen:", cloudflare["company"])
print("Anzahl Präfixe:", len(cloudflare["prefixes"]))

# Subnetzmasken konvertieren
print(cidr2mask("192.168.1.0/24"))  # 255.255.255.0
print(mask2cidr("255.255.255.0"))    # 24
```

---

## 💸 Projekt unterstützen

**[☕️ Kauf mir einen Kaffee](https://KekikAkademi.org/Kahve)**

## 🌐 Urheberrecht und Lizenz

* *Copyright (C) 2023 - 2026 by* [keyiflerolsun](https://github.com/keyiflerolsun) ❤️️
* Lizenziert unter den Bedingungen der [GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007](https://github.com/keyiflerolsun/KeeneticPy/blob/main/LICENSE).

## ♻️ Kontakt

*Kontaktieren Sie mich gerne via **Telegram**:* [@keyiflerolsun](https://t.me/KekikKahve)

> *Entwickelt für* **[@KekikAkademi](https://t.me/KekikAkademi)**
