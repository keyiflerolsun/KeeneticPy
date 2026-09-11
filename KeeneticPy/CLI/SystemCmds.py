# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from rich.table import Table
from rich.panel import Panel
from rich       import box
from .Base      import console, get_router, run_watchable
from ..Libs     import format_bytes, parse_dsl_stats, parse_mesh_nodes, describe_host_link
import argparse

def cmd_info(args:argparse.Namespace):
    with get_router(args) as router:
        sys_info = router.system()
        ver_info = router.version()
        wan_ips  = router.global_ip()
        net      = router.internet_status()

        table = Table(title="📡 Keenetic Cihaz Bilgisi", show_header=False, border_style="cyan", box=box.ROUNDED)
        table.add_column("Özellik", style="bold yellow")
        table.add_column("Değer", style="white")

        table.add_row("Model", ver_info.get("model", "N/A"))
        table.add_row("Sürüm", ver_info.get("title", ver_info.get("release", "N/A")))
        table.add_row("Cihaz Adı", ver_info.get("device", "N/A"))
        table.add_row("Çalışma Süresi (Uptime)", f"{sys_info.get('uptime', 0)} sn")
        table.add_row("Bellek (RAM)", f"{format_bytes(sys_info.get('cpuload', 0))} (Load: {sys_info.get('cpuload', 0)}%)")
        table.add_row("WAN IPv4", wan_ips.get("ipv4") or "[dim]Yok[/dim]")
        table.add_row("WAN IPv6", wan_ips.get("ipv6") or "[dim]Yok[/dim]")

        gateway_iface = net.get("gateway", {}).get("interface", "-")
        net_status    = f"[green]✓ Bağlı[/green] (Gateway: {gateway_iface})" if net.get("internet") else "[red]✗ Bağlantı Yok[/red]"
        table.add_row("İnternet Durumu", net_status)
        console.print(table)

def cmd_hosts(args:argparse.Namespace):
    with get_router(args) as router:
        def render():
            hosts_data = router.hosts().get("host", [])
            table      = Table(title=f"💻 Bağlı Cihazlar ({len(hosts_data)})", border_style="green", box=box.ROUNDED)
            table.add_column("İsim / Hostname", style="bold white")
            table.add_column("IP Adresi", style="cyan")
            table.add_column("MAC Adresi", style="magenta")
            table.add_column("Arayüz", style="yellow")
            table.add_column("Bağlantı", style="magenta")
            table.add_column("Durum", style="green")
            table.add_column("Trafik (Rx / Tx)", style="blue")

            for h in hosts_data:
                name   = h.get("name") or h.get("hostname") or "Bilinmeyen"
                ip     = h.get("ip", "-")
                mac    = h.get("mac", "-")
                iface  = h.get("interface", {}).get("name", "-")
                link   = describe_host_link(h.get("mws"))
                status = "[green]Aktif[/green]" if h.get("active") else "[dim]Pasif[/dim]"
                rx_tx  = f"{format_bytes(h.get('rxbytes', 0))} / {format_bytes(h.get('txbytes', 0))}"
                table.add_row(name, ip, mac, iface, link, status, rx_tx)

            return table

        run_watchable(args, render)

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
            def render():
                parsed  = parse_dsl_stats(router.dsl_stats())
                general = Table(title="Genel", show_header=False, border_style="cyan", box=box.ROUNDED)
                general.add_column("Özellik", style="bold yellow")
                general.add_column("Değer", style="white")
                for key, val in parsed["general"].items():
                    general.add_row(key, val)

                def pairs_table(title, rows):
                    t = Table(title=title, border_style="cyan", box=box.ROUNDED)
                    t.add_column("Metrik", style="bold yellow")
                    t.add_column("DS", style="cyan")
                    t.add_column("US", style="magenta")
                    for key, (ds, us) in rows:
                        t.add_row(key, ds, us)
                    return t

                # Uzun DS/US listesi tek parça olunca terminal boyunu aşıp kaydırma
                # gerektiriyordu; Genel tablonun boyuna yakın kalması için ikiye bölüp
                # yan yana yerleştiriyoruz.
                pair_items = list(parsed["pairs"].items())
                mid        = (len(pair_items) + 1) // 2
                pairs1     = pairs_table("DS / US (1/2)", pair_items[:mid])
                pairs2     = pairs_table("DS / US (2/2)", pair_items[mid:])

                grid = Table.grid(padding=(0, 1))
                grid.add_column()
                grid.add_column()
                grid.add_column()
                grid.add_row(general, pairs1, pairs2)
                return Panel(grid, title="📶 DSL İstatistikleri", border_style="cyan")

            run_watchable(args, render)

def cmd_mesh(args:argparse.Namespace):
    with get_router(args) as router:
        if getattr(args, "mesh_action", None) == "reboot":
            if router.reboot_mesh_node(args.cid):
                console.print(f"[green]✓[/green] Mesh üyesi ({args.cid}) yeniden başlatılıyor...")
            else:
                console.print("[red]✗[/red] Mesh üyesi yeniden başlatılamadı.")
            return

        def render():
            nodes = parse_mesh_nodes(router.mesh_nodes())
            if not nodes:
                return "[yellow]Mesh üyesi bulunamadı (Mesh desteklenmiyor veya tek cihazlısın).[/yellow]"

            table = Table(title=f"🕸️  Mesh Üyeleri ({len(nodes)})", border_style="green", box=box.ROUNDED)
            table.add_column("İsim", style="bold white")
            table.add_column("IP", style="cyan")
            table.add_column("Model", style="yellow")
            table.add_column("Mod", style="magenta")
            table.add_column("Durum", style="green")
            table.add_column("İstemci", style="blue")
            table.add_column("CPU / RAM", style="white")
            table.add_column("Backhaul", style="white")

            for n in nodes:
                status = "[green]Bağlı[/green]" if n["connected"] else "[red]Bağlantı Yok[/red]"
                load   = f"{n['cpuload']}% / {n['memory_pct']}%" if n["cpuload"] is not None else "-"
                table.add_row(n["name"], n["ip"] or "-", n["model"] or "-", n["mode"] or "-", status, str(n["associations"]), load, n["backhaul"] or "-")

            return table

        run_watchable(args, render)
