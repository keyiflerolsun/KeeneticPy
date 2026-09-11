# KeeneticPy 📡

<div align="center">

**[ English ](README.md)** • **[ Türkçe ](README.tr.md)** • **[ Русский ](README.ru.md)** • **[ Deutsch ](README.de.md)**

[![Boyut](https://img.shields.io/github/repo-size/keyiflerolsun/KeeneticPy?logo=git&logoColor=white&label=Boyut)](#)
[![Görüntülenme](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/keyiflerolsun/KeeneticPy&title=Görüntülenme)](#)
<a href="https://KekikAkademi.org/Kahve" target="_blank"><img src="https://img.shields.io/badge/☕️-Kahve Ismarla-ffdd00" title="☕️ Kahve Ismarla" style="padding-left:5px;"></a>

[![PyPI](https://img.shields.io/pypi/v/KeeneticPy?logo=pypi&logoColor=white&label=PyPI)](https://pypi.org/project/KeeneticPy)
[![PyPI - Yüklenme](https://img.shields.io/pypi/dm/KeeneticPy?logo=pypi&logoColor=white&label=Yüklenme)](https://pypi.org/project/KeeneticPy)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/KeeneticPy?logo=pypi&logoColor=white&label=Wheel)](https://pypi.org/project/KeeneticPy)
[![Python Version](https://img.shields.io/pypi/pyversions/KeeneticPy?logo=python&logoColor=white&label=Python)](#)
[![Lisans](https://img.shields.io/pypi/l/KeeneticPy?logo=gnu&logoColor=white&label=Lisans)](#)
[![Durum](https://img.shields.io/pypi/status/KeeneticPy?logo=windowsterminal&logoColor=white&label=Durum)](#)
[![PyPI Yükle](https://github.com/keyiflerolsun/KeeneticPy/actions/workflows/PyPI.yml/badge.svg)](https://github.com/keyiflerolsun/KeeneticPy/actions/workflows/PyPI.yml)

</div>

**Keenetic Router'lar için Modern, Async/Sync Python Kütüphanesi ve CLI Aracı (KeeneticOS RCI)**

Keenetic router'ların `RCI` (Remote Control Interface) API'si üzerinden yönetilmesini sağlayan; **WireGuard/VPN ilke bazlı yönlendirme (Domain & ASN routing)**, **otomatik CIDR rota senkronizasyonu**, **4G/LTE modem ve SMS yönetimi**, **cihaz bant genişliği/hız sınırlaması**, **Prometheus metrik sunucusu** ve akıllı yedekleme sunan modern Python kütüphanesi ve CLI aracı.

---

## ✨ Özellikler

* ⚡ **Sync & Async Desteği**: Hem `Keenetic` hem de `AsyncKeenetic` (`async with`) ile tam uyum (Home Assistant ve FastAPI dostu).
* 🛡️ **Hafif ve Bağımsız**: Ağır ve hantal bağımlılıklardan arındırılmış; yalnızca `httpx` ve `rich` üzerine kurulu modern mimari.
* 🌐 **BGP & İlke Bazlı Yönlendirme (PBR)**: Alan adlarını (Cloudflare DoH) veya ASN IP bloklarını (RIPE Stat API) tek komutla WireGuard / VPN arayüzlerine ilke bazlı yönlendirme.
* 🔄 **Toplu Rota Senkronizasyonu**: URL'den veya yerel dosyalardan IP/CIDR listelerini router'a otomatik senkronize etme, listeden kalkan eski rotaları otomatik temizleme (`route sync`).
* 📶 **4G/LTE Hücresel Modem & SMS**: Sinyal gücü (RSRP, RSRQ, SINR, Band, Operatör) izleme, gelen SMS'leri okuma, SMS gönderme ve USSD sorguları çalıştırma.
* 👥 **İstemci Yönetimi & Hız Sınırı**: Cihaz bazlı indirme/yükleme hız sınırı koyma, internet erişimini tek tıkla engelleme/açma ve statik DHCP rezervasyonu.
* 📊 **Dahili Prometheus Exporter**: Router ve bağlı cihaz metriklerini Prometheus ve Grafana için canlı HTTP endpoint olarak sunma (`keenetic exporter`).
* 💻 **Zengin CLI (Terminal Aracı)**: Router'ınızı doğrudan terminalden yönetebileceğiniz kapsamlı komut seti.
* 💾 **Akıllı Yedekleme**: Firmware ve startup-config dosyalarını zip formatında tarih ve rotasyonla arşivleme.

---

## 🚀 Kurulum

```bash
# pip ile kurulum
pip install -U KeeneticPy

# uv ile kurulum
uv add KeeneticPy
```

---

## 💻 CLI Kullanımı (Terminal)

Kurulum sonrasında `keenetic` komutu doğrudan terminalinizde kullanılabilir:

```bash
# Router durumunu, CPU/RAM yükünü ve WAN IP'lerini görüntüleme
keenetic --password "şifreniz" info

# Bağlı istemcileri ve gerçek zamanlı veri akışını (Rx/Tx) listeleme
keenetic --password "şifreniz" hosts

# Discord alan adını Wireguard arayüzüne yönlendirme
keenetic --password "şifreniz" route add-domain discord.com --interface Wireguard0

# Cloudflare ASN (13335) bloklarını Wireguard'a yönlendirme
keenetic --password "şifreniz" route add-asn 13335 --interface Wireguard0

# URL veya dosyadan toplu rota senkronize etme (eski kayıtları otomatik siler)
keenetic --password "şifreniz" route sync https://antifilter.download/list/allyouneed.lst --interface Wireguard0

# Cihaza indirme/yükleme hız sınırı koyma (5 Mbps download, 1 Mbps upload)
keenetic --password "şifreniz" client limit AA:BB:CC:DD:EE:FF --rx 5000 --tx 1000

# Cihazın internet erişimini engelleme / engeli kaldırma
keenetic --password "şifreniz" client block AA:BB:CC:DD:EE:FF
keenetic --password "şifreniz" client unblock AA:BB:CC:DD:EE:FF

# Cihaza statik IP / DHCP rezervasyonu atama
keenetic --password "şifreniz" client bind AA:BB:CC:DD:EE:FF 192.168.1.100 -n "Masaustu-PC"

# 4G/LTE modem sinyal durumu ve SMS yönetimi
keenetic --password "şifreniz" modem status
keenetic --password "şifreniz" modem sms-list
keenetic --password "şifreniz" modem sms-send +905551234567 "Sunucu uyarisi"
keenetic --password "şifreniz" modem ussd "*100#"

# Prometheus metrik sunucusunu 9100 portunda başlatma
keenetic --password "şifreniz" exporter --port 9100

# Router yedeği alma (son 5 yedeği saklar)
keenetic --password "şifreniz" backup --keep 5

# Router'ı uzaktan yeniden başlatma
keenetic --password "şifreniz" reboot
```

> **İpucu:** Çevre değişkenleri ile şifre girmeyi otomatikleştirebilirsiniz:
> ```bash
> export KEENETIC_USER="admin"
> export KEENETIC_PASSWORD="modem_sifreniz"
> export KEENETIC_PANEL="http://192.168.1.1"
> ```

---

## 📝 Python Kullanımı

### 1. Senkron Kullanım (`Keenetic`)

```python
from KeeneticPy import Keenetic, set_speed_limit, set_client_access, get_modem_info, send_sms

with Keenetic(user="admin", password="password", panel="http://192.168.1.1") as router:
    # Cihaz ve Sistem Bilgileri
    print("Sürüm:", router.version())
    print("WAN IP:", router.global_ip())

    # Domain bazlı VPN Rotası Ekleme
    router.add_route_with_domain("discord.com", interface="Wireguard0")

    # İstemciye 10 Mbps hız limiti koyma
    set_speed_limit(router, "aa:bb:cc:dd:ee:ff", rx_kbps=10000, tx_kbps=5000)

    # 4G/LTE Sinyal Kalitesini Kontrol Etme
    modem = get_modem_info(router)
    print("Operatör:", modem.get("operator"))
    print("RSRP Sinyal:", modem.get("rsrp"))

    # SMS Bildirimi Gönderme
    send_sms(router, "+905551234567", "Router yedekleme islemi tamamlandi.")

    # Yedek Alma
    router.backup(max_backups=3)
```

---

### 2. Asenkron Kullanım (`AsyncKeenetic` - Home Assistant / FastAPI)

```python
import asyncio
from KeeneticPy import AsyncKeenetic, sync_static_routes, parse_route_entries, fetch_route_text

async def main():
    async with AsyncKeenetic(user="admin", password="password", panel="http://192.168.1.1") as router:
        hosts = await router.hosts()
        print("Bağlı cihaz sayısı:", len(hosts.get("host", [])))

        # URL'den IP listesini çekip Wireguard'a senkronize etme
        ham_rotalar = fetch_route_text("https://example.com/routes.txt")
        girisler = parse_route_entries(ham_rotalar)
        sonuc = await sync_static_routes(router, girisler, interface="Wireguard0")
        print("Senkronizasyon sonucu:", sonuc)

asyncio.run(main())
```

---

### 3. BGP & DNS Çözümleme Araçları (`BGPTools`)

```python
from KeeneticPy import domain2ip, asn2cidr, cidr2mask, mask2cidr

# Alan adını DoH üzerinden çözümler ve alt ağları hesaplar
bilgi = domain2ip("github.com")
print(bilgi["ipler"])
print(bilgi["subnetler"])

# ASN numarasına ait prefix'leri resmi RIPE Stat API'den çeker
cloudflare = asn2cidr(13335)
print("Şirket:", cloudflare["company"])
print("Prefix adedi:", len(cloudflare["prefixes"]))

# Alt ağ dönüşümleri
print(cidr2mask("192.168.1.0/24"))  # 255.255.255.0
print(mask2cidr("255.255.255.0"))    # 24
```

---

## 💸 Bağış Yap

**[☕️ Kahve Ismarla](https://KekikAkademi.org/Kahve)**

## 🌐 Telif Hakkı ve Lisans

* *Copyright (C) 2023 - 2026 by* [keyiflerolsun](https://github.com/keyiflerolsun) ❤️️
* [GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007](https://github.com/keyiflerolsun/KeeneticPy/blob/main/LICENSE) koşullarına göre lisanslanmıştır.

## ♻️ İletişim

*Benimle iletişime geçmek isterseniz, **Telegram**'dan mesaj göndermekten çekinmeyin;* [@keyiflerolsun](https://t.me/KekikKahve)

> **[@KekikAkademi](https://t.me/KekikAkademi)** *için yazılmıştır..*
