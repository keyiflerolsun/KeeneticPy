# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

class KeeneticError(Exception):
    """Base exception for KeeneticPy."""
    pass

class KeeneticAuthError(KeeneticError):
    """Authentication or authorization failure."""
    pass

class KeeneticRCIError(KeeneticError):
    """Keenetic RCI command execution failure."""
    pass

class KeeneticConnectionError(KeeneticError):
    """Connection failure to router panel."""
    pass
