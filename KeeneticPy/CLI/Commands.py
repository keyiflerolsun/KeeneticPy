# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from .SystemCmds  import cmd_info, cmd_hosts, cmd_backup, cmd_reboot, cmd_dsl, cmd_mesh
from .NetworkCmds import cmd_route, cmd_client, cmd_modem, cmd_exporter
from .Base        import add_watch_args
import argparse

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="keenetic", description="KeeneticOS CLI Yönetim Aracı")
    parser.add_argument("-u", "--user", default=None, help="Router kullanıcı adı")
    parser.add_argument("-p", "--password", default=None, help="Router şifresi")
    parser.add_argument("--panel", default=None, help="Router panel URL'i (varsayılan: http://192.168.1.1)")
    parser.add_argument("--timeout", type=float, default=10.0, help="İstek zaman aşımı süresi")

    sub = parser.add_subparsers(dest="subcommand", required=True)

    p_info = sub.add_parser("info", help="Cihaz ve sistem durumunu göster")
    p_info.set_defaults(func=cmd_info)

    p_hosts = sub.add_parser("hosts", help="Bağlı hotspot cihazlarını listele")
    add_watch_args(p_hosts)
    p_hosts.set_defaults(func=cmd_hosts)

    p_route = sub.add_parser("route", help="Statik ve VPN rota yönetimi")
    r_sub   = p_route.add_subparsers(dest="route_action", required=True)
    r_list  = r_sub.add_parser("list", help="Rotaları listele")
    r_list.set_defaults(func=cmd_route)
    r_clean = r_sub.add_parser("clean", help="Tekrarlanan rotaları temizle")
    r_clean.set_defaults(func=cmd_route)

    r_dom = r_sub.add_parser("add-domain", help="Domain bazlı rota ekle")
    r_dom.add_argument("domain", help="Hedef domain adı (örn: discord.com)")
    r_dom.add_argument("-i", "--interface", default="Wireguard0", help="Hedef arayüz")
    r_dom.set_defaults(func=cmd_route)

    r_asn = r_sub.add_parser("add-asn", help="ASN prefix rotaları ekle")
    r_asn.add_argument("asn", help="ASN numarası (örn: 13335)")
    r_asn.add_argument("-i", "--interface", default="Wireguard0", help="Hedef arayüz")
    r_asn.set_defaults(func=cmd_route)

    r_sync = r_sub.add_parser("sync", help="Dosya veya URL'den toplu rota senkronize et")
    r_sync.add_argument("source", help="Yerel dosya yolu veya HTTP/HTTPS URL")
    r_sync.add_argument("-i", "--interface", default="Wireguard0", help="Hedef arayüz")
    r_sync.add_argument("-t", "--tag", default="AutoSync", help="Senkronizasyon etiketi")
    r_sync.set_defaults(func=cmd_route)

    p_client = sub.add_parser("client", help="Cihaz hız sınırı ve erişim yönetimi")
    c_sub    = p_client.add_subparsers(dest="client_action", required=True)
    c_lim    = c_sub.add_parser("limit", help="Cihaza indirme/yükleme hız sınırı koy")
    c_lim.add_argument("mac", help="Cihaz MAC adresi")
    c_lim.add_argument("--rx", type=int, default=0, help="İndirme sınırı (kbps, 0=limitsiz)")
    c_lim.add_argument("--tx", type=int, default=0, help="Yükleme sınırı (kbps, 0=limitsiz)")
    c_lim.set_defaults(func=cmd_client)

    c_blk = c_sub.add_parser("block", help="Cihazın internetini engelle")
    c_blk.add_argument("mac", help="Cihaz MAC adresi")
    c_blk.set_defaults(func=cmd_client)

    c_ublk = c_sub.add_parser("unblock", help="Cihazın internet engelini kaldır")
    c_ublk.add_argument("mac", help="Cihaz MAC adresi")
    c_ublk.set_defaults(func=cmd_client)

    c_bind = c_sub.add_parser("bind", help="Cihaza statik IP / DHCP rezervasyonu ata")
    c_bind.add_argument("mac", help="Cihaz MAC adresi")
    c_bind.add_argument("ip", help="Sabit IP adresi")
    c_bind.add_argument("-n", "--name", default=None, help="Cihaz adı")
    c_bind.set_defaults(func=cmd_client)

    p_modem = sub.add_parser("modem", help="4G/LTE hücresel modem ve SMS yönetimi")
    m_sub   = p_modem.add_subparsers(dest="modem_action", required=True)
    m_stat  = m_sub.add_parser("status", help="Modem ve sinyal durumunu göster")
    m_stat.add_argument("-i", "--interface", default=None, help="Hücresel arayüz")
    m_stat.set_defaults(func=cmd_modem)

    m_smsl = m_sub.add_parser("sms-list", help="Gelen SMS kutusunu listele")
    m_smsl.set_defaults(func=cmd_modem)

    m_smss = m_sub.add_parser("sms-send", help="SMS gönder")
    m_smss.add_argument("phone", help="Telefon numarası")
    m_smss.add_argument("text", help="Mesaj içeriği")
    m_smss.set_defaults(func=cmd_modem)

    m_ussd = m_sub.add_parser("ussd", help="USSD komutu çalıştır (örn: *100#)")
    m_ussd.add_argument("code", help="USSD kodu")
    m_ussd.set_defaults(func=cmd_modem)

    p_exp = sub.add_parser("exporter", help="Prometheus metrik sunucusunu başlat")
    p_exp.add_argument("-p", "--port", type=int, default=9100, help="Sunucu portu")
    p_exp.add_argument("--host", default="0.0.0.0", help="Dinlenecek IP adresi")
    p_exp.set_defaults(func=cmd_exporter)

    p_backup = sub.add_parser("backup", help="Yedek al (firmware + config)")
    p_backup.add_argument("-k", "--keep", type=int, default=5, help="Saklanacak yedek sayısı")
    p_backup.add_argument("-d", "--dir", default=".", help="Hedef klasör")
    p_backup.set_defaults(func=cmd_backup)

    p_reboot = sub.add_parser("reboot", help="Router'ı yeniden başlat")
    p_reboot.add_argument("-y", "--yes", action="store_true", help="Onay sormadan yeniden başlat")
    p_reboot.set_defaults(func=cmd_reboot)

    p_dsl   = sub.add_parser("dsl", help="DSL işlemleri")
    d_sub   = p_dsl.add_subparsers(dest="dsl_action", required=True)
    d_stats = d_sub.add_parser("stats", help="DSL istatistiklerini göster")
    add_watch_args(d_stats)
    d_stats.set_defaults(func=cmd_dsl)
    d_reset = d_sub.add_parser("reset", help="DSL bağlantısını sıfırla")
    d_reset.set_defaults(func=cmd_dsl)

    p_mesh   = sub.add_parser("mesh", help="Mesh Wi-Fi System üyelerini göster")
    add_watch_args(p_mesh)
    p_mesh.set_defaults(func=cmd_mesh)
    mesh_sub = p_mesh.add_subparsers(dest="mesh_action")
    m_reboot = mesh_sub.add_parser("reboot", help="Mesh üyesini yeniden başlat")
    m_reboot.add_argument("cid", help="Mesh üyesi CID değeri (mesh komutunun çıktısından alınır)")
    m_reboot.set_defaults(func=cmd_mesh)

    return parser

def main():
    parser = build_parser()
    args   = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
