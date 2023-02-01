# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from requests import Session
from hashlib  import md5, sha256

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