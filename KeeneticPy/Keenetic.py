# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from Kekik.cli import konsol
from httpx     import Client
from hashlib   import md5, sha256
from zipfile   import ZipFile, ZIP_DEFLATED
from os        import remove, listdir
from datetime  import datetime
from Kekik     import slugify
from .         import cidr2mask, asn2cidr, domain2ip

class Keenetic:
    def __init__(self, user:str="admin", password:str="", ip:str="192.168.1.1"):
        self.__oturum = Client()
        self.__panel  = f"http://{ip}"
        self.__rci    = f"{self.__panel}/rci/"

        self._yetki   = self.__yetkilendir(user, password)
        if not self._yetki:
            assert False, "Yetkisiz Erişim."

    def __yetkilendir(self, user:str, password:str) -> bool:
        istek = self.__oturum.get(f"{self.__panel}/auth")
        if istek.status_code == 200:
            return True

        cihaz = istek.headers["X-NDM-Realm"]
        token = istek.headers["X-NDM-Challenge"]

        __sifre = f"{user}:{cihaz}:{password}"
        __sifre = md5(__sifre.encode("utf-8")).hexdigest()
        __sifre = f"{token}{__sifre}"
        __sifre = sha256(__sifre.encode("utf-8")).hexdigest()

        istek = self.__oturum.post(
            url  = f"{self.__panel}/auth",
            json = {"login":user, "password":__sifre}
        )

        return istek.status_code == 200

    def interface(self) -> dict:
        return self.__oturum.get(f"{self.__rci}show/interface").json()

    def system(self) -> dict:
        return self.__oturum.get(f"{self.__rci}show/system").json()

    def version(self) -> dict:
        return self.__oturum.get(f"{self.__rci}show/version").json()

    def hosts(self) -> dict:
        return self.__oturum.get(f"{self.__rci}show/ip/hotspot").json()

    def dsl_stats(self) -> dict:
        return self.__oturum.post(
            url  = f"{self.__rci}",
            json = {"parse": "more proc:/driver/ensoc_dsl/dsl_stats"}
        ).json()

    def dsl_reset(self) -> bool:
        kapama_istegi = self.__oturum.post(
            url  = f"{self.__rci}",
            json = [
                {"interface" : {"Dsl0": {"up": {"no": True}}}},
                {"system"    : {"configuration": {"save": True}}}
            ]
        )

        acma_istegi = self.__oturum.post(
            url  = f"{self.__rci}",
            json = [
                {"interface" : {"Dsl0": {"up": {"no": False}}}},
                {"system"    : {"configuration": {"save": True}}}
            ]
        )

        return kapama_istegi.status_code == 200 and acma_istegi.status_code == 200

    def global_ip(self) -> dict:
        veri = self.__oturum.post(
            url  = f"{self.__rci}",
            json = {
                "ip"     : {"http":{"ssl":{"acme":{"list":{}}}}},
                "show"   : {"clock":{"date":{}},"schedule":{},"internet":{"status":{}},"version":{},"system":{},"interface":{},"ip":{"name-server":{},"route":{},"hotspot":{"details":"wireless"}},"rc":{"interface":{},"service":{},"user":{},"components":{"auto-update":{}},"ip":{"http":{}},"dlna":{}},"ndns":{},"acme":{},"dyndns":{},"ping-check":{},"cifs":{},"printers":{},"ipv6":{"addresses":{},"prefixes":{},"routes":{}},"dlna":{},"usb":{},"media":{}},
                "ls"     : {},
                "whoami" : {}
            }
        ).json()

        for ls in veri["ls"]["entry"].copy().keys():
            if ls in ["flash:", "temp:", "proc:", "sys:", "log", "running-config", "startup-config", "default-config", "ndm:", "debug:", "storage:"]:
                del veri["ls"]["entry"][ls]

        return {
            # "whoami"  : veri["whoami"],
            # "keedns"  : veri["ip"]["http"]["ssl"]["acme"]["list"]["certificate"],
            # "devices" : veri["ls"]["entry"],
            # "sbm"     : veri["show"]["cifs"]["share"],
            # "dlna"    : veri["show"]["dlna"]["directory"],
            "ipv4"    : veri["show"]["interface"]["PPPoE0"]["address"],
            "ipv6"    : [adres for adres in veri["show"]["ipv6"]["addresses"]["address"] if adres["interface"] == "PPPoE0"][0]["address"],
        }

    def __zip_tarih_al(self, file_name:str) -> datetime:
        tarih_str = file_name.split("_")[-1].replace(".zip", "")
        return datetime.strptime(tarih_str, "%d-%m-%Y")

    def backup(self, maks_backup=5) -> str:
        if not self._yetki:
            assert False, "Yetkisiz Erişim."

        tarih       = datetime.now().strftime("%d-%m-%Y")
        cihaz       = self.version()
        zip_dosyasi = f"{slugify(cihaz['description'])}_{slugify(cihaz['hw_version'])}_{tarih}.zip"
        fw          = "firmware.bin"
        config      = "startup-config.txt"

        fw_istek = self.__oturum.get(f"{self.__panel}/ci/firmware")
        if fw_istek.status_code != 200:
            konsol.log(f"[red][!] {fw} İndirme Hatası: {fw_istek.status_code}")
        else:
            with open(fw, "wb") as dosya:
                dosya.write(fw_istek.content)
            konsol.log(f"[green][+] {fw} indirildi!")

        config_istek = self.__oturum.get(f"{self.__panel}/ci/startup-config")
        if config_istek.status_code != 200:
            konsol.log(f"[red][!] {config} İndirme Hatası: {config_istek.status_code}")
        else:
            with open(config, "wb") as dosya:
                dosya.write(config_istek.content)
            konsol.log(f"[green][+] {config} indirildi!")

        with ZipFile(zip_dosyasi, "w", ZIP_DEFLATED) as arsiv:
            arsiv.write(fw)
            arsiv.write(config)

        remove(config)
        remove(fw)

        yedekler = sorted(
            [dosya for dosya in listdir() if dosya.endswith(".zip") and dosya.startswith(zip_dosyasi.split("_")[0])],
            key     = self.__zip_tarih_al,
            reverse = True
        )

        for yedek in yedekler[maks_backup:][::-1]:
            remove(yedek)
            konsol.log(f"[yellow][~] {yedek} dosyası silindi!")

        konsol.log(f"[green][+] {zip_dosyasi} başarıyla oluşturuldu!")

        return zip_dosyasi

    def get_static_routes(self) -> list[dict[str, str]]:
        return self.__oturum.get(
            url  = f"{self.__rci}",
            json = {"show":{"ip":{"route":{}}}}
        ).json().get("ip", {}).get("route", [])

    def add_static_route(self, comment:str, host:str=None, network:str=None, mask:str=None, interface:str="Wireguard2") -> bool:
        payload = None

        if host:
            payload = {
                "comment"   : comment,
                "interface" : interface,
                "host"      : host
            }

        if network and mask:
            payload = {
                "comment"   : comment,
                "interface" : interface,
                "network"   : network,
                "mask"      : mask
            }

        if not payload:
            assert False, "Lütfen host ya da network ve mask bilgisini girin."

        istek = self.__oturum.post(
            url  = f"{self.__rci}",
            json = [
                {"ip":{"route":payload}},
                {"system":{"configuration":{"save":{}}}}
            ]
        )

        return istek.status_code == 200

    def add_route_with_asn(self, asn:str|int, interface:str="Wireguard2"):
        asn_data = asn2cidr(asn)
        if not asn_data:
            assert False, f"ASN {asn} için CIDR bilgisine ulaşılamıyor."

        for prefix in asn_data["prefixes"]:
            veri = {"comment": asn_data["company"], "network": prefix.split("/")[0], "mask": cidr2mask(prefix), "interface": interface}
            if self.add_static_route(**veri):
                konsol.log(f"[green][+] {prefix} » {veri.get('comment')} » başarıyla eklendi!")
            else:
                konsol.log(f"[red][!] {prefix} » {veri.get('comment')} » eklenemedi!")

    def add_route_with_domain(self, domain:str, interface:str="Wireguard2") -> bool:
        domain_data = domain2ip(domain)

        if not domain_data:
            assert False, f"Domain {domain} için IP bilgisine ulaşılamıyor."

        if not domain_data["ipler"]:
            assert False, f"Domain {domain} için IP bilgisine ulaşılamıyor."

        if domain_data.get("subnetler"):
            for subnet in domain_data["subnetler"]:
                veri = {"comment": domain_data["domain"], "network": subnet.split("/")[0], "mask": cidr2mask(subnet), "interface": interface}
                if self.add_static_route(**veri):
                    konsol.log(f"[green][+] {subnet} » {veri.get('comment')} » başarıyla eklendi!")
                else:
                    konsol.log(f"[red][!] {subnet} » {veri.get('comment')} » eklenemedi!")

        for ip in domain_data["ipler"]:
            veri = {"comment": domain_data["domain"], "host": ip, "interface": interface}
            if self.add_static_route(**veri):
                konsol.log(f"[green][+] {ip} » {veri.get('comment')} » başarıyla eklendi!")
            else:
                konsol.log(f"[red][!] {ip} » {veri.get('comment')} » eklenemedi!")

    def del_static_route(self, comment:str, host:str=None, network:str=None, mask:str=None, interface:str="Wireguard2") -> bool:
        payload = None

        if host:
            payload = {
                "comment"   : comment,
                "interface" : interface,
                "host"      : host
            }

        if network and mask:
            payload = {
                "comment"   : comment,
                "interface" : interface,
                "network"   : network,
                "mask"      : mask
            }

        if not payload:
            assert False, "Lütfen host ya da network ve mask bilgisini girin."

        payload["no"] = True

        istek = self.__oturum.post(
            url  = f"{self.__rci}",
            json = [
                {"ip":{"route":payload}},
                {"system":{"configuration":{"save":{}}}}
            ]
        )

        return istek.status_code == 200