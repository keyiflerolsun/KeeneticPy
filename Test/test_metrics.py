# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from unittest.mock           import MagicMock
from KeeneticPy.Libs.Metrics import generate_prometheus_metrics, make_metrics_handler

def test_generate_prometheus_metrics():
    mock_router                     = MagicMock()
    mock_router.system.return_value = {
        "uptime"   : 14400,
        "cpuload"  : 15,
        "memtotal" : 262144,
        "memfree"  : 131072
    }
    mock_router.version.return_value = {
        "model"   : "Hero",
        "release" : "4.02",
        "device"  : "Keenetic-Hero"
    }
    mock_router.hosts.return_value = {
        "host" : [
            {"name" : "MyPhone", "mac" : "11:22:33:44:55:66", "ip" : "192.168.1.10", "active" : True, "rxbytes" : 5000, "txbytes" : 10000}
        ]
    }

    metrics = generate_prometheus_metrics(mock_router)

    assert "keenetic_uptime_seconds 14400" in metrics
    assert "keenetic_cpu_load_percent 15" in metrics
    assert 'keenetic_device_info{model="Hero",release="4.02",device="Keenetic-Hero"} 1' in metrics
    assert "keenetic_clients_total 1" in metrics
    assert "keenetic_clients_active 1" in metrics
    assert 'keenetic_client_rx_bytes{mac="11:22:33:44:55:66",ip="192.168.1.10",name="MyPhone"} 5000' in metrics

def test_metrics_handler_routing():
    mock_router                      = MagicMock()
    mock_router.system.return_value  = {"uptime" : 100}
    mock_router.version.return_value = {}
    mock_router.hosts.return_value   = {"host" : []}

    handler_cls = make_metrics_handler(mock_router)
    assert handler_cls is not None
