# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from Kekik.cli import konsol
from requests  import Session
from hashlib   import md5, sha256
from zipfile   import ZipFile, ZIP_DEFLATED
from os        import remove, listdir
from datetime  import datetime
from Kekik     import slugify

class Keenetic:
    def __init__(self, kullanici:str="admin", sifre:str="", ip:str="192.168.1.1"):
        self.__oturum = Session()
        self.__panel  = f"http://{ip}"
        self.__rci    = f"{self.__panel}/rci/"

        self._yetki   = self.__yetkilendir(kullanici, sifre)
        if not self._yetki:
            assert False, "Yetkisiz Erişim."

    def __yetkilendir(self, kullanici:str, sifre:str) -> bool:
        istek = self.__oturum.get(f"{self.__panel}/auth")
        if istek.status_code == 200:
            return True

        cihaz = istek.headers["X-NDM-Realm"]
        token = istek.headers["X-NDM-Challenge"]

        __sifre = f"{kullanici}:{cihaz}:{sifre}"
        __sifre = md5(__sifre.encode("utf-8")).hexdigest()
        __sifre = f"{token}{__sifre}"
        __sifre = sha256(__sifre.encode("utf-8")).hexdigest()

        istek = self.__oturum.post(
            url  = f"{self.__panel}/auth",
            json = {"login":kullanici, "password":__sifre}
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

    def __zip_tarih_al(self, dosya_adi:str) -> datetime:
        tarih_str = dosya_adi.split("_")[-1].replace(".zip", "")
        return datetime.strptime(tarih_str, "%d-%m-%Y")

    def backup(self, maksimum_yedek=5) -> str:
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

        for yedek in yedekler[maksimum_yedek:][::-1]:
            remove(yedek)
            konsol.log(f"[yellow][~] {yedek} dosyası silindi!")

        konsol.log(f"[green][+] {zip_dosyasi} başarıyla oluşturuldu!")

        return zip_dosyasi