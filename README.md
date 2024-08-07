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

### Keenetic Sınıfını Oluşturma

Keenetic router'ınıza bağlanmak için aşağıdaki gibi bir `Keenetic` sınıfı örneği oluşturun:

```python
from KeeneticPy import Keenetic

modem = Keenetic(user="admin", password="cokomellisifre", panel="http://192.168.1.1")
```

### Yedekleme Yapma

Modem yapılandırma yedeği oluşturmak için `backup` fonksiyonunu kullanabilirsiniz. Aşağıdaki örnekte, maksimum 2 yedek dosyası saklanacaktır:

```python
modem.backup(maks_backup=2)
```

### Sistem ve Sürüm Bilgilerini Görüntüleme

Modeminizin sistem ve sürüm bilgilerini almak için `system` ve `version` metodlarını kullanabilirsiniz:

```python
print(modem.system())
print(modem.version())
```

### Arayüz Bilgilerini Görüntüleme

Modeminizin DSL ve PPPoE arayüz bilgilerini görüntülemek için:

```python
print(modem.interface()["Dsl0"])
print(modem.interface()["PPPoE0"])
```

### Global IP Bilgilerini Almak

Router'ınızın global IP bilgilerini almak için:

```python
print(modem.global_ip())
```

### DSL İstatistiklerini Görüntüleme

DSL bağlantınızla ilgili detaylı istatistikleri almak için:

```python
print("n".join(modem.dsl_stats()["parse"]["message"]))
```

### Hotspot Üzerindeki Bağlı Cihazları Listeleme

Modeminizdeki Hotspot üzerinden bağlı cihazları görüntülemek için:

```python
print(modem.hosts())
```

### DSL Bağlantısını Sıfırlama

DSL bağlantınızı sıfırlamak için:

```python
print(modem.dsl_reset())
```

### Statik Rotaları Yönetme

#### Arayüz İsimlerini Listeleme:

Modeminizin tanımlı arayüz isimlerini, türlerini ve açıklamalarını almak için:

```python
interface_names = modem.get_interface_names()
print(interface_names)
```

#### Statik Rota Ekleme:

Bir statik rota eklemek için `add_static_route` metodunu kullanabilirsiniz:
> Arayüz (interface) ismini doğru şekilde ayarladığınızdan emin olun. Arayüz isimlerini [.get_interface_names()](#arayüz-i̇simlerini-listeleme) fonksiyonunu kullanarak öğrenebilirsiniz.

```python
modem.add_static_route(comment="örnek.io", host="192.168.1.100", interface="Wireguard2")
```

#### Statik Rota Silme:

Eklenmiş bir statik rotayı silmek için `del_static_route` metodunu kullanabilirsiniz:

```python
modem.del_static_route(comment="örnek.io", host="192.168.1.100", interface="Wireguard2")
```

#### **kwargs Kullanımı ile Statik Rota Silme:

Mevcut statik rotalarınızdan belirli bir yoruma sahip olanları silmek için:

```python
routes = modem.get_static_routes()

for route in routes:
    print(route)
    if route.get("comment") == "bakalim.io":
        print(modem.del_static_route(**route))
```

### Domain veya ASN ile Rota Ekleme

#### Domain ile Rota Ekleme:

Belirli bir domain için statik rota eklemek:
> Arayüz (interface) ismini doğru şekilde ayarladığınızdan emin olun. Arayüz isimlerini [.get_interface_names()](#arayüz-i̇simlerini-listeleme) fonksiyonunu kullanarak öğrenebilirsiniz.

```python
modem.add_route_with_domain(domain="example.com", interface="Wireguard2")
```

#### ASN ile Rota Ekleme:

Belirli bir ASN için statik rota eklemek:
> Arayüz (interface) ismini doğru şekilde ayarladığınızdan emin olun. Arayüz isimlerini [.get_interface_names()](#arayüz-i̇simlerini-listeleme) fonksiyonunu kullanarak öğrenebilirsiniz.

```python
modem.add_route_with_asn(asn=32934, interface="Wireguard2")
```

***

Bu örnekler, KeeneticPy paketini nasıl kullanabileceğinizi ve çeşitli modem işlevlerini nasıl yönetebileceğinizi gösterir. Daha fazla bilgi için kaynak koduna göz atabilirsiniz.

***

## 💸 Bağış Yap

**[☕️ Kahve Ismarla](https://KekikAkademi.org/Kahve)**

## 🌐 Telif Hakkı ve Lisans

* *Copyright (C) 2023 by* [keyiflerolsun](https://github.com/keyiflerolsun) ❤️️
* [GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007](https://github.com/keyiflerolsun/KeeneticPy/blob/master/LICENSE) *Koşullarına göre lisanslanmıştır..*

## ♻️ İletişim

*Benimle iletişime geçmek isterseniz, **Telegram**'dan mesaj göndermekten çekinmeyin;* [@keyiflerolsun](https://t.me/KekikKahve)

##

> **[@KekikAkademi](https://t.me/KekikAkademi)** *için yazılmıştır..*