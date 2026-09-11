# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from http.server import HTTPServer, BaseHTTPRequestHandler
from contextlib  import suppress
import logging

logger = logging.getLogger("KeeneticPy.metrics")

def generate_prometheus_metrics(router) -> str:
    """Generate Prometheus exposition text format for router metrics."""
    lines = []

    with suppress(Exception):
        sys_data = router.system()
        if "uptime" in sys_data:
            lines.append("# HELP keenetic_uptime_seconds Router uptime in seconds")
            lines.append("# TYPE keenetic_uptime_seconds gauge")
            lines.append(f"keenetic_uptime_seconds {sys_data['uptime']}")

        if "cpuload" in sys_data:
            lines.append("# HELP keenetic_cpu_load_percent Current CPU load percentage")
            lines.append("# TYPE keenetic_cpu_load_percent gauge")
            lines.append(f"keenetic_cpu_load_percent {sys_data['cpuload']}")

        if "memfree" in sys_data and "memtotal" in sys_data:
            used = sys_data["memtotal"] - sys_data["memfree"]
            lines.append("# HELP keenetic_memory_used_bytes Used system memory in bytes")
            lines.append("# TYPE keenetic_memory_used_bytes gauge")
            lines.append(f"keenetic_memory_used_bytes {used * 1024}")

    with suppress(Exception):
        ver_data = router.version()
        model    = ver_data.get("model", "unknown")
        release  = ver_data.get("release", "unknown")
        device   = ver_data.get("device", "unknown")
        lines.append("# HELP keenetic_device_info Device hardware and firmware details")
        lines.append("# TYPE keenetic_device_info gauge")
        lines.append(f'keenetic_device_info{{model="{model}",release="{release}",device="{device}"}} 1')

    with suppress(Exception):
        hosts_data = router.hosts().get("host", [])
        active_cnt = sum(1 for h in hosts_data if h.get("active"))

        lines.append("# HELP keenetic_clients_total Total number of registered hotspot clients")
        lines.append("# TYPE keenetic_clients_total gauge")
        lines.append(f"keenetic_clients_total {len(hosts_data)}")

        lines.append("# HELP keenetic_clients_active Number of actively connected clients")
        lines.append("# TYPE keenetic_clients_active gauge")
        lines.append(f"keenetic_clients_active {active_cnt}")

        lines.append("# HELP keenetic_client_rx_bytes Total received bytes by client")
        lines.append("# TYPE keenetic_client_rx_bytes counter")
        lines.append("# HELP keenetic_client_tx_bytes Total transmitted bytes by client")
        lines.append("# TYPE keenetic_client_tx_bytes counter")

        for h in hosts_data:
            mac    = h.get("mac", "")
            ip     = h.get("ip", "")
            name   = (h.get("name") or h.get("hostname") or "unknown").replace('"', "")
            rx     = h.get("rxbytes", 0)
            tx     = h.get("txbytes", 0)
            labels = f'mac="{mac}",ip="{ip}",name="{name}"'
            lines.append(f"keenetic_client_rx_bytes{{{labels}}} {rx}")
            lines.append(f"keenetic_client_tx_bytes{{{labels}}} {tx}")

    return "\n".join(lines) + "\n"

def make_metrics_handler(router):
    class MetricsHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in ("/metrics", "/"):
                body = generate_prometheus_metrics(router).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            return

    return MetricsHandler

def run_metrics_server(router, port:int=9100, host:str="0.0.0.0"):
    """Start standalone Prometheus metrics HTTP server."""
    handler_cls = make_metrics_handler(router)
    server      = HTTPServer((host, port), handler_cls)
    logger.info(f"Serving Prometheus metrics at http://{host}:{port}/metrics")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
