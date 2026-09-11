# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from rich.console import Console
from ..Core       import Keenetic, KeeneticError
import argparse
import os
import sys

console = Console()

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
