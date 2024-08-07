# KeeneticPy

[![Boyut](https://img.shields.io/github/repo-size/keyiflerolsun/KeeneticPy?logo=git&logoColor=white&label=Boyut)](#)
[![Görüntülenme](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/keyiflerolsun/KeeneticPy&title=Görüntülenme)](#)
<a href="https://KekikAkademi.org/Kahve" target="_blank"><img src="https://img.shields.io/badge/☕️-Kahve Ismarla-ffdd00" title="☕️ Kahve Ismarla" style="padding-left:5px;"></a>

[![PyPI](https://img.shields.io/pypi/v/KeeneticPy?logo=pypi&logoColor=white&label=PyPI)](https://pypi.org/project/KeeneticPy)
[![PyPI - Yüklenme](https://img.shields.io/pypi/dm/KeeneticPy?logo=pypi&logoColor=white&label=Yüklenme)](https://pypi.org/project/KeeneticPy)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/KeeneticPy?logo=pypi&logoColor=white&label=Wheel)](https://pypi.org/project/KeeneticPy)

[![Python Version](https://img.shields.io/pypi/pyversions/KeeneticPy?logo=python&logoColor=white&label=Python)](#)
[![Lisans](https://img.shields.io/pypi/l/KeeneticPy?logo=gnu&logoColor=white&label=Lisans)](#)
[![Durum](https://img.shields.io/pypi/status/KeeneticPy?logo=windowsterminal&logoColor=white&label=Durum)](#)

[![PyPI Yükle](https://github.com/keyiflerolsun/KeeneticPy/actions/workflows/pypiYukle.yml/badge.svg)](https://github.com/keyiflerolsun/KeeneticPy/actions/workflows/pypiYukle.yml)

**Python Lib for Keenetic Routers**

> _`RCI` / `PROC`_

[![ForTheBadge made-with-python](https://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![ForTheBadge built-with-love](https://ForTheBadge.com/images/badges/built-with-love.svg)](https://GitHub.com/keyiflerolsun/)

## 🚀 Kurulum

```bash
# Yüklemek
pip install KeeneticPy

# Güncellemek
pip install -U KeeneticPy
```

## <img src="https://www.akashtrehan.com/assets/images/emoji/terminal.png" height="32" align="center"> Kullanım

```python
from Kekik.cli  import konsol
from KeeneticPy import Keenetic

modem = Keenetic(sifre="cokomellisifre")

modem.backup(maksimum_yedek=2)

konsol.print(modem.system())
konsol.print(modem.version())

konsol.print(modem.interface()["Dsl0"])
konsol.print(modem.interface()["PPPoE0"])

konsol.print(modem.global_ip())

konsol.print("\n".join(modem.dsl_stats()["parse"]["message"]))

konsol.print(modem.hosts())

konsol.print(modem.dsl_reset())

konsol.print(modem.get_static_routes())

konsol.print(modem.add_static_route(comment="bakalim.io", host="145.53.10.71", interface="Wireguard2"))

konsol.print(modem.add_static_route(comment="bakalim.io", network="145.53.10.0", mask="255.255.255.0", interface="Wireguard2"))

konsol.print(modem.del_static_route(comment="bakalim.io", network="145.53.10.0", mask="255.255.255.0", interface="Wireguard2"))

konsol.print(modem.del_static_route(comment="bakalim.io", host="145.53.10.71", interface="Wireguard2"))

for route in modem.get_static_routes():
    konsol.log(route)
    if route.get("comment") == "bakalim.io":
        konsol.print(modem.del_static_route(**route))
        break
```

## 💸 Bağış Yap

**[☕️ Kahve Ismarla](https://KekikAkademi.org/Kahve)**

## 🌐 Telif Hakkı ve Lisans

* *Copyright (C) 2023 by* [keyiflerolsun](https://github.com/keyiflerolsun) ❤️️
* [GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007](https://github.com/keyiflerolsun/KeeneticPy/blob/master/LICENSE) *Koşullarına göre lisanslanmıştır..*

## ♻️ İletişim

*Benimle iletişime geçmek isterseniz, **Telegram**'dan mesaj göndermekten çekinmeyin;* [@keyiflerolsun](https://t.me/KekikKahve)

##

> **[@KekikAkademi](https://t.me/KekikAkademi)** *için yazılmıştır..*