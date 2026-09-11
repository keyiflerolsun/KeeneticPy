# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from rich.table import Table
from rich.panel import Panel
from .Base      import console, get_router
from ..Libs     import parse_route_entries, fetch_route_text, sync_static_routes, set_speed_limit, set_client_access, set_dhcp_binding, get_modem_info, get_sms_messages, send_sms, send_ussd, run_metrics_server
import argparse

def cmd_route(args:argparse.Namespace):
    with get_router(args) as router:
        if args.route_action == "list":
            routes = router.get_static_routes()
            table  = Table(title=f"🛣️ Statik Rotalar ({len(routes)})", border_style="blue")
            table.add_column("Hedef", style="bold cyan")
            table.add_column("Maske", style="magenta")
            table.add_column("Arayüz", style="yellow")
            table.add_column("Açıklama", style="white")

            for r in routes:
                target = r.get("network") or r.get("host") or "-"
                table.add_row(target, r.get("mask", "-"), r.get("interface", "-"), r.get("comment", ""))
            console.print(table)

        elif args.route_action == "add-domain":
            console.print(f"[cyan]'{args.domain}'[/cyan] çözümleniyor...")
            try:
                added = router.add_route_with_domain(args.domain, interface=args.interface)
                console.print(f"[green]✓[/green] {len(added)} rota eklendi: {', '.join(added)}")
            except Exception as e:
                console.print(f"[bold red]Hata:[/bold red] {e}")

        elif args.route_action == "add-asn":
            console.print(f"[cyan]AS{args.asn}[/cyan] prefixleri alınıyor...")
            try:
                added = router.add_route_with_asn(args.asn, interface=args.interface)
                console.print(f"[green]✓[/green] {len(added)} prefix eklendi.")
            except Exception as e:
                console.print(f"[bold red]Hata:[/bold red] {e}")

        elif args.route_action == "clean":
            deleted = router.clean_multiple_routes()
            console.print(f"[green]✓[/green] {deleted} adet mükerrer rota temizlendi.")

        elif args.route_action == "sync":
            console.print(f"[cyan]'{args.source}'[/cyan] kaynağından rotalar alınıyor...")
            try:
                raw_text = fetch_route_text(args.source)
                entries  = parse_route_entries(raw_text)
                res      = sync_static_routes(router, entries, interface=args.interface, tag=args.tag)
                console.print(f"[green]✓[/green] Senkronize edildi: {len(res['added'])} eklendi, {len(res['removed'])} silindi (Toplam: {res['total']})")
            except Exception as e:
                console.print(f"[bold red]Hata:[/bold red] {e}")

def cmd_client(args:argparse.Namespace):
    with get_router(args) as router:
        if args.client_action == "limit":
            if set_speed_limit(router, args.mac, rx_kbps=args.rx, tx_kbps=args.tx):
                console.print(f"[green]✓[/green] {args.mac} için hız sınırı ayarlandı (Rx: {args.rx}k, Tx: {args.tx}k).")
            else:
                console.print("[bold red]Hata:[/bold red] Hız sınırı ayarlanamadı.")

        elif args.client_action in ("block", "unblock"):
            permit = (args.client_action == "unblock")
            if set_client_access(router, args.mac, permit=permit):
                durum = "açıldı" if permit else "engellendi"
                console.print(f"[green]✓[/green] {args.mac} erişimi {durum}.")
            else:
                console.print("[bold red]Hata:[/bold red] Erişim durumu değiştirilemedi.")

        elif args.client_action == "bind":
            if set_dhcp_binding(router, args.mac, args.ip, name=args.name):
                console.print(f"[green]✓[/green] {args.mac} -> {args.ip} statik DHCP olarak bağlandı.")
            else:
                console.print("[bold red]Hata:[/bold red] DHCP rezervasyonu yapılamadı.")

def cmd_modem(args:argparse.Namespace):
    with get_router(args) as router:
        if args.modem_action == "status":
            info = get_modem_info(router, interface=args.interface)
            if not info:
                console.print("[yellow]Hücresel modem bulunamadı veya bağlı değil.[/yellow]")
                return

            table = Table(title="📶 4G/LTE Modem Durumu", show_header=False, border_style="green")
            table.add_column("Özellik", style="bold cyan")
            table.add_column("Değer", style="white")
            for k, v in info.items():
                table.add_row(k.capitalize(), str(v))
            console.print(table)

        elif args.modem_action == "sms-list":
            msgs = get_sms_messages(router)
            if not msgs:
                console.print("[yellow]Gelen SMS kutusu boş.[/yellow]")
                return

            table = Table(title=f"📩 SMS Mesajları ({len(msgs)})", border_style="cyan")
            table.add_column("Gönderen", style="bold yellow")
            table.add_column("Tarih", style="magenta")
            table.add_column("Mesaj", style="white")
            for m in msgs:
                table.add_row(m.get("phone", "-"), m.get("date", "-"), m.get("text", "-"))
            console.print(table)

        elif args.modem_action == "sms-send":
            if send_sms(router, args.phone, args.text):
                console.print(f"[green]✓[/green] SMS '{args.phone}' numarasına gönderildi.")
            else:
                console.print("[bold red]Hata:[/bold red] SMS gönderilemedi.")

        elif args.modem_action == "ussd":
            resp = send_ussd(router, args.code)
            if resp:
                console.print(Panel(resp, title=f"USSD Yanıtı ({args.code})", border_style="cyan"))
            else:
                console.print("[yellow]USSD yanıtı alınamadı.[/yellow]")

def cmd_exporter(args:argparse.Namespace):
    with get_router(args) as router:
        console.print(f"[cyan]Prometheus exporter başlatılıyor: http://{args.host}:{args.port}/metrics[/cyan]")
        run_metrics_server(router, port=args.port, host=args.host)
