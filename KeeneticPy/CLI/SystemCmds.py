# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from rich.table import Table
from rich.panel import Panel
from .Base      import console, get_router
from ..Libs     import format_bytes
import argparse

def cmd_info(args:argparse.Namespace):
    with get_router(args) as router:
        sys_info = router.system()
        ver_info = router.version()
        wan_ips  = router.global_ip()

        table = Table(title="📡 Keenetic Cihaz Bilgisi", show_header=False, border_style="cyan")
        table.add_column("Özellik", style="bold yellow")
        table.add_column("Değer", style="white")

        table.add_row("Model", ver_info.get("model", "N/A"))
        table.add_row("Sürüm", ver_info.get("title", ver_info.get("release", "N/A")))
        table.add_row("Cihaz Adı", ver_info.get("device", "N/A"))
        table.add_row("Çalışma Süresi (Uptime)", f"{sys_info.get('uptime', 0)} sn")
        table.add_row("Bellek (RAM)", f"{format_bytes(sys_info.get('cpuload', 0))} (Load: {sys_info.get('cpuload', 0)}%)")
        table.add_row("WAN IPv4", wan_ips.get("ipv4") or "[dim]Yok[/dim]")
        table.add_row("WAN IPv6", wan_ips.get("ipv6") or "[dim]Yok[/dim]")
        console.print(table)

def cmd_hosts(args:argparse.Namespace):
    with get_router(args) as router:
        hosts_data = router.hosts().get("host", [])
        table      = Table(title=f"💻 Bağlı Cihazlar ({len(hosts_data)})", border_style="green")
        table.add_column("İsim / Hostname", style="bold white")
        table.add_column("IP Adresi", style="cyan")
        table.add_column("MAC Adresi", style="magenta")
        table.add_column("Arayüz", style="yellow")
        table.add_column("Durum", style="green")
        table.add_column("Trafik (Rx / Tx)", style="blue")

        for h in hosts_data:
            name   = h.get("name") or h.get("hostname") or "Bilinmeyen"
            ip     = h.get("ip", "-")
            mac    = h.get("mac", "-")
            iface  = h.get("interface", {}).get("name", "-")
            status = "[green]Aktif[/green]" if h.get("active") else "[dim]Pasif[/dim]"
            rx_tx  = f"{format_bytes(h.get('rxbytes', 0))} / {format_bytes(h.get('txbytes', 0))}"
            table.add_row(name, ip, mac, iface, status, rx_tx)

        console.print(table)

def cmd_backup(args:argparse.Namespace):
    with get_router(args) as router:
        console.print("[cyan]Router yedeği alınıyor...[/cyan]")
        path = router.backup(max_backups=args.keep, target_dir=args.dir)
        console.print(f"[green]✓[/green] Yedek kaydedildi: [bold]{path}[/bold]")

def cmd_reboot(args:argparse.Namespace):
    if not args.yes:
        confirm = console.input("[bold red]Router yeniden başlatılsın mı? (e/H): [/bold red]")
        if confirm.strip().lower() not in ("e", "y"):
            console.print("[yellow]İşlem iptal edildi.[/yellow]")
            return

    with get_router(args) as router:
        if router.reboot():
            console.print("[green]✓[/green] Router yeniden başlatılıyor...")
        else:
            console.print("[red]✗[/red] Yeniden başlatma komutu başarısız.")

def cmd_dsl(args:argparse.Namespace):
    with get_router(args) as router:
        if args.dsl_action == "reset":
            if router.dsl_reset():
                console.print("[green]✓[/green] DSL arayüzü başarıyla sıfırlandı.")
            else:
                console.print("[red]✗[/red] DSL sıfırlama başarısız.")
        else:
            stats = router.dsl_stats()
            console.print(Panel(str(stats), title="DSL İstatistikleri", border_style="cyan"))
