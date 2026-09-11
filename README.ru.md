# KeeneticPy 📡

<div align="center">

**[ English ](README.md)** • **[ Türkçe ](README.tr.md)** • **[ Русский ](README.ru.md)** • **[ Deutsch ](README.de.md)**

[![Размер](https://img.shields.io/github/repo-size/keyiflerolsun/KeeneticPy?logo=git&logoColor=white&label=Размер)](#)
[![Просмотры](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/keyiflerolsun/KeeneticPy&title=Просмотры)](#)
<a href="https://KekikAkademi.org/Kahve" target="_blank"><img src="https://img.shields.io/badge/☕️-Купить%20кофе-ffdd00" title="☕️ Купить кофе" style="padding-left:5px;"></a>

[![PyPI](https://img.shields.io/pypi/v/KeeneticPy?logo=pypi&logoColor=white&label=PyPI)](https://pypi.org/project/KeeneticPy)
[![PyPI - Загрузки](https://img.shields.io/pypi/dm/KeeneticPy?logo=pypi&logoColor=white&label=Загрузки)](https://pypi.org/project/KeeneticPy)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/KeeneticPy?logo=pypi&logoColor=white&label=Wheel)](https://pypi.org/project/KeeneticPy)
[![Python Version](https://img.shields.io/pypi/pyversions/KeeneticPy?logo=python&logoColor=white&label=Python)](#)
[![Лицензия](https://img.shields.io/pypi/l/KeeneticPy?logo=gnu&logoColor=white&label=Лицензия)](#)
[![Статус](https://img.shields.io/pypi/status/KeeneticPy?logo=windowsterminal&logoColor=white&label=Статус)](#)
[![PyPI Publish](https://github.com/keyiflerolsun/KeeneticPy/actions/workflows/PyPI.yml/badge.svg)](https://github.com/keyiflerolsun/KeeneticPy/actions/workflows/PyPI.yml)

</div>

**Современная асинхронная и синхронная библиотека Python и CLI-утилита для роутеров Keenetic (KeeneticOS RCI)**

KeeneticPy — это продвинутая библиотека Python и консольная утилита для управления роутерами под управлением KeeneticOS через официальный API `RCI` (Remote Control Interface). Предоставляет возможности **политической маршрутизации (PBR) для WireGuard / VPN (по доменам и ASN)**, **пакетной синхронизации списков CIDR (Antifilter и др.)**, **управления 4G/LTE модемами и SMS**, **ограничения скорости клиентов**, **встроенного экспортера метрик Prometheus** и автоматического резервного копирования.

---

## ✨ Возможности

* ⚡ **Синхронный и асинхронный клиенты**: Полная поддержка `Keenetic` и `AsyncKeenetic` (`async with`), готовая интеграция для **Home Assistant** и **FastAPI**.
* 🛡️ **Без тяжелых зависимостей**: Быстрая и легковесная архитектура исключительно на базе `httpx` и `rich`.
* 🌐 **BGP и маршрутизация по доменам / ASN**: Направление доменов (через Cloudflare DoH) или целых префиксов автономных систем (через официальный RIPE Stat API) в интерфейс WireGuard / VPN одной командой.
* 🔄 **Пакетная синхронизация маршрутов**: Загрузка и обновление списков статических маршрутов по URL или из локального файла с автоматической очисткой устаревших записей (`route sync`).
* 📶 **Управление 4G/LTE модемом и SMS**: Диагностика параметров сигнала (RSRP, RSRQ, SINR, Band, оператор), чтение входящих SMS, отправка SMS и выполнение USSD-запросов (например, баланс `*100#`).
* 👥 **Контроль клиентов и шейпинг скорости**: Ограничение скорости приема и отдачи (Rx/Tx) по MAC-адресу, блокировка доступа в интернет и привязка статических IP-адресов по DHCP.
* 📊 **Встроенный Prometheus Exporter**: Экспорт метрик роутера, сети и подключенных устройств для дашбордов Grafana (`keenetic exporter`).
* 💻 **Полнофункциональный CLI**: Управление всеми функциями роутера напрямую из терминала.
* 💾 **Умное резервное копирование**: Скачивание архивов с прошивкой и файлом конфигурации `startup-config.txt` с ротацией версий.

---

## 🚀 Установка

```bash
# С помощью pip
pip install -U KeeneticPy

# С помощью uv
uv add KeeneticPy
```

---

## 💻 Использование в командной строке (CLI)

После установки команда `keenetic` сразу доступна в терминале:

```bash
# Информация о роутере, нагрузке CPU/RAM и WAN IP
keenetic --password "ваш_пароль" info

# Список подключенных клиентов и объем трафика в реальном времени (Rx/Tx)
keenetic --password "ваш_пароль" hosts

# Направить трафик домена в туннель WireGuard
keenetic --password "ваш_пароль" route add-domain discord.com --interface Wireguard0

# Направить префиксы Cloudflare ASN (13335) в WireGuard
keenetic --password "ваш_пароль" route add-asn 13335 --interface Wireguard0

# Синхронизировать список маршрутов из сети (Antifilter) или файла
keenetic --password "ваш_пароль" route sync https://antifilter.download/list/allyouneed.lst --interface Wireguard0

# Ограничить скорость клиента (5 Мбит/с входящая, 1 Мбит/с исходящая)
keenetic --password "ваш_пароль" client limit AA:BB:CC:DD:EE:FF --rx 5000 --tx 1000

# Заблокировать / разблокировать доступ устройства в интернет
keenetic --password "ваш_пароль" client block AA:BB:CC:DD:EE:FF
keenetic --password "ваш_пароль" client unblock AA:BB:CC:DD:EE:FF

# Назначить статический IP / DHCP привязку
keenetic --password "ваш_пароль" client bind AA:BB:CC:DD:EE:FF 192.168.1.100 -n "Рабочий-ПК"

# Диагностика сигнала 4G/LTE модема и работа с SMS
keenetic --password "ваш_пароль" modem status
keenetic --password "ваш_пароль" modem sms-list
keenetic --password "ваш_пароль" modem sms-send +79991234567 "Оповещение сервера"
keenetic --password "ваш_пароль" modem ussd "*100#"

# Запустить экспортер метрик для Prometheus на порту 9100
keenetic --password "ваш_пароль" exporter --port 9100

# Создать резервную копию роутера (сохранить последние 5)
keenetic --password "ваш_пароль" backup --keep 5

# Перезагрузить роутер удаленно
keenetic --password "ваш_пароль" reboot
```

> **Совет:** Чтобы не передавать учетные данные в аргументах команды, используйте переменные окружения:
> ```bash
> export KEENETIC_USER="admin"
> export KEENETIC_PASSWORD="ваш_пароль"
> export KEENETIC_PANEL="http://192.168.1.1"
> ```

---

## 📝 Использование в Python

### 1. Синхронный клиент (`Keenetic`)

```python
from KeeneticPy import Keenetic, set_speed_limit, set_client_access, get_modem_info, send_sms

with Keenetic(user="admin", password="password", panel="http://192.168.1.1") as router:
    # Версия прошивки и внешний IP
    print("Версия ПО:", router.version())
    print("Внешний IP:", router.global_ip())

    # Добавление маршрута для домена через WireGuard
    router.add_route_with_domain("discord.com", interface="Wireguard0")

    # Установка лимита скорости для смартфона (10 Мбит/с загрузка, 5 Мбит/с отдача)
    set_speed_limit(router, "aa:bb:cc:dd:ee:ff", rx_kbps=10000, tx_kbps=5000)

    # Проверка уровня сигнала 4G/LTE
    modem = get_modem_info(router)
    print("Оператор:", modem.get("operator"))
    print("Уровень RSRP:", modem.get("rsrp"))

    # Отправка SMS уведомления
    send_sms(router, "+79991234567", "Бэкап роутера успешно создан.")

    # Создание резервной копии
    router.backup(max_backups=3)
```

---

### 2. Асинхронный клиент (`AsyncKeenetic` — Home Assistant / FastAPI)

```python
import asyncio
from KeeneticPy import AsyncKeenetic, sync_static_routes, parse_route_entries, fetch_route_text

async def main():
    async with AsyncKeenetic(user="admin", password="password", panel="http://192.168.1.1") as router:
        hosts = await router.hosts()
        print("Подключено устройств:", len(hosts.get("host", [])))

        # Синхронизация внешнего списка маршрутов в Wireguard
        raw_routes = fetch_route_text("https://example.com/routes.txt")
        entries = parse_route_entries(raw_routes)
        result = await sync_static_routes(router, entries, interface="Wireguard0")
        print("Результат синхронизации:", result)

asyncio.run(main())
```

---

### 3. Утилиты BGP и поиска подсетей (`BGPTools`)

```python
from KeeneticPy import domain2ip, asn2cidr, cidr2mask, mask2cidr

# Разрешение домена через DoH и группировка по подсетям CIDR
info = domain2ip("github.com")
print("IP-адреса:", info["ipler"])
print("Подсети:", info["subnetler"])

# Запрос IPv4 префиксов по номеру ASN из официального API RIPE Stat
cloudflare = asn2cidr(13335)
print("Организация:", cloudflare["company"])
print("Количество префиксов:", len(cloudflare["prefixes"]))

# Преобразование сетевых масок
print(cidr2mask("192.168.1.0/24"))  # 255.255.255.0
print(mask2cidr("255.255.255.0"))    # 24
```

---

## 💸 Поддержка проекта

**[☕️ Купить мне кофе](https://KekikAkademi.org/Kahve)**

## 🌐 Авторские права и лицензия

* *Copyright (C) 2023 - 2026 by* [keyiflerolsun](https://github.com/keyiflerolsun) ❤️️
* Распространяется на условиях лицензии [GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007](https://github.com/keyiflerolsun/KeeneticPy/blob/main/LICENSE).

## ♻️ Контакты

*Вы можете связаться со мной в **Telegram**:* [@keyiflerolsun](https://t.me/KekikKahve)

> *Написано для* **[@KekikAkademi](https://t.me/KekikAkademi)**
