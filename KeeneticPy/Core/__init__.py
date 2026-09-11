# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from .Exceptions import KeeneticError, KeeneticAuthError, KeeneticRCIError, KeeneticConnectionError
from .Async      import AsyncKeenetic
from contextlib  import suppress
import asyncio
import threading

class Keenetic:
    """Synchronous KeeneticOS RCI API Client powered by AsyncKeenetic engine."""
    is_async = False

    def __init__(self, user:str="admin", password:str="", panel:str="http://192.168.1.1", timeout:float=10.0, verify:bool=False, transport=None):
        self._closed = False
        self._loop   = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()

        try:
            self._async_client = AsyncKeenetic(user=user, password=password, panel=panel, timeout=timeout, verify=verify, transport=transport)
            self._yetki        = self._run(self._async_client.authenticate())
            if not self._yetki:
                self.close()
                raise KeeneticAuthError("Failed to authenticate with Keenetic router.")
        except Exception:
            self.close()
            raise

    def _run(self, coro, timeout:float=15.0):
        """Execute a coroutine on the client's dedicated background event loop."""
        if getattr(self, "_closed", False) or not hasattr(self, "_loop") or not self._loop.is_running():
            raise RuntimeError("Keenetic client event loop is not running.")
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=timeout)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        """Close asynchronous HTTP session and stop the event loop."""
        if getattr(self, "_closed", False):
            return
        self._closed = True

        with suppress(Exception):
            if hasattr(self, "_async_client") and hasattr(self, "_loop") and self._loop.is_running():
                future = asyncio.run_coroutine_threadsafe(self._async_client.close(), self._loop)
                future.result(timeout=2.0)

        with suppress(Exception):
            if hasattr(self, "_loop") and self._loop.is_running():
                self._loop.call_soon_threadsafe(self._loop.stop)
                self._thread.join(timeout=1.0)

    def __getattr__(self, name:str):
        """Delegate attribute and method calls to the underlying AsyncKeenetic client."""
        attr = getattr(self._async_client, name)
        if callable(attr):
            def sync_wrapper(*args, **kwargs):
                res = attr(*args, **kwargs)
                if asyncio.iscoroutine(res):
                    return self._run(res)
                return res
            return sync_wrapper
        return attr
