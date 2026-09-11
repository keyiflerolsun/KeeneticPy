# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from rich.console import Console, Group
from rich.live    import Live
from datetime     import datetime
from contextlib   import suppress
from ..Core       import Keenetic, KeeneticError
import argparse
import os
import sys
import time

console = Console()

def add_watch_args(parser:argparse.ArgumentParser):
    """Add --watch/-w live refresh flags to a subcommand parser."""
    parser.add_argument("-w", "--watch", action="store_true", help="Canlı (live) görünüm, sürekli yenile")
    parser.add_argument("-n", "--interval", type=float, default=2.0, help="Yenileme aralığı (saniye, varsayılan: 2)")

def run_watchable(args:argparse.Namespace, render_fn):
    """Print a renderable once, or keep it live-refreshing until Ctrl+C when --watch is set."""
    if not getattr(args, "watch", False):
        with console.status("[cyan]Router'dan veri alınıyor...[/cyan]", spinner="dots"):
            renderable = render_fn()
        console.print(renderable)
        return

    def framed():
        ts = datetime.now().strftime("%H:%M:%S")
        return Group(render_fn(), f"[dim]🔄 Son güncelleme: {ts} · Ctrl+C ile çıkış[/dim]")

    with Live(framed(), console=console, refresh_per_second=4) as live:
        with suppress(KeyboardInterrupt):
            while True:
                time.sleep(args.interval)
                live.update(framed())

def get_router(args:argparse.Namespace) -> Keenetic:
    """Instantiate Keenetic client from arguments or environment variables."""
    user     = getattr(args, "user", None) or os.getenv("KEENETIC_USER", "admin")
    password = getattr(args, "password", None) or os.getenv("KEENETIC_PASSWORD", "")
    panel    = getattr(args, "panel", None) or os.getenv("KEENETIC_PANEL", "http://192.168.1.1")
    timeout  = getattr(args, "timeout", 10.0) or 10.0
    try:
        return Keenetic(user=user, password=password, panel=panel, timeout=timeout)
    except KeeneticError as err:
        console.print(f"[bold red]Hata:[/bold red] {err}")
        sys.exit(1)
