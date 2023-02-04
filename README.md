# KeeneticPy

![Repo Boyutu](https://img.shields.io/github/repo-size/keyiflerolsun/KeeneticPy?logo=git&logoColor=white)
![Görüntülenme](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/keyiflerolsun/KeeneticPy&title=Görüntülenme)
<a href="https://KekikAkademi.org/Kahve" target="_blank"><img src="https://img.shields.io/badge/☕️-Kahve Ismarla-ffdd00" title="☕️ Kahve Ismarla" style="padding-left:5px;"></a>

![Python Version](https://img.shields.io/pypi/pyversions/KeeneticPy?logo=python&logoColor=white)
![License](https://img.shields.io/pypi/l/KeeneticPy?logo=gnu&logoColor=white)
![Status](https://img.shields.io/pypi/status/KeeneticPy?logo=windowsterminal&logoColor=white)

![PyPI](https://img.shields.io/pypi/v/KeeneticPy?logo=pypi&logoColor=white)
![PyPI - Downloads](https://img.shields.io/pypi/dm/KeeneticPy?logo=pypi&logoColor=white)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/KeeneticPy?logo=pypi&logoColor=white)

**Python Lib for Keenetic Routers**

> _`RCI` / `PROC`_

[![ForTheBadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![ForTheBadge built-with-love](http://ForTheBadge.com/images/badges/built-with-love.svg)](https://GitHub.com/keyiflerolsun/)

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

hero = Keenetic(sifre="cokomellisifre")

konsol.print(hero.system())
konsol.print(hero.version())

konsol.print(hero.interface()["Dsl0"])
konsol.print(hero.interface()["PPPoE0"])

konsol.print(hero.global_ip())

konsol.print("\n".join(hero.dsl_stats()["parse"]["message"]))

konsol.print(hero.hosts())

konsol.print(hero.dsl_reset())
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
