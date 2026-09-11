# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from unittest.mock  import patch, MagicMock
from KeeneticPy.CLI import build_parser, get_router, cmd_info, cmd_hosts, cmd_route, cmd_client, cmd_modem, cmd_backup, cmd_reboot, cmd_dsl, cmd_mesh, run_watchable

def test_cli_parser_global_args():
    parser = build_parser()
    args   = parser.parse_args(["-u", "myuser", "-p", "mypass", "--panel", "http://10.0.0.1", "--timeout", "15.0", "info"])
    assert args.user == "myuser"
    assert args.password == "mypass"
    assert args.panel == "http://10.0.0.1"
    assert args.timeout == 15.0
    assert args.subcommand == "info"

def test_cli_parser_subcommands():
    parser = build_parser()

    args = parser.parse_args(["route", "sync", "http://example.com/routes.txt", "-i", "WG0", "-t", "CF"])
    assert args.subcommand == "route"
    assert args.route_action == "sync"
    assert args.source == "http://example.com/routes.txt"
    assert args.tag == "CF"

    args = parser.parse_args(["client", "limit", "aa:bb:cc:dd:ee:ff", "--rx", "5000", "--tx", "1000"])
    assert args.subcommand == "client"
    assert args.client_action == "limit"
    assert args.rx == 5000

    args = parser.parse_args(["client", "block", "aa:bb:cc:dd:ee:ff"])
    assert args.client_action == "block"

    args = parser.parse_args(["client", "bind", "aa:bb:cc:dd:ee:ff", "192.168.1.50", "-n", "PC"])
    assert args.client_action == "bind"
    assert args.ip == "192.168.1.50"

    args = parser.parse_args(["modem", "status"])
    assert args.subcommand == "modem"
    assert args.modem_action == "status"

    args = parser.parse_args(["modem", "sms-send", "+90555", "Hello"])
    assert args.modem_action == "sms-send"
    assert args.phone == "+90555"

    args = parser.parse_args(["exporter", "--port", "9200", "--host", "127.0.0.1"])
    assert args.subcommand == "exporter"
    assert args.port == 9200

def test_cli_parser_watch_flags():
    parser = build_parser()

    args = parser.parse_args(["hosts", "-w", "-n", "5"])
    assert args.watch    is True
    assert args.interval == 5.0

    args = parser.parse_args(["mesh", "--watch"])
    assert args.watch    is True
    assert args.interval == 2.0

    args = parser.parse_args(["dsl", "stats", "-w"])
    assert args.watch is True

    args = parser.parse_args(["dsl", "reset"])
    assert not hasattr(args, "watch")

def test_run_watchable_no_watch():
    parser = build_parser()
    args   = parser.parse_args(["hosts"])
    render = MagicMock(return_value="table")

    with patch("KeeneticPy.CLI.Base.console") as mock_console:
        mock_console.status.return_value.__enter__.return_value = None
        run_watchable(args, render)

    render.assert_called_once()
    mock_console.print.assert_called_once_with("table")

def test_run_watchable_watch_stops_on_interrupt():
    parser = build_parser()
    args   = parser.parse_args(["hosts", "-w", "-n", "0"])
    render = MagicMock(return_value="table")

    with patch("KeeneticPy.CLI.Base.time.sleep", side_effect=KeyboardInterrupt):
        with patch("KeeneticPy.CLI.Base.Live") as mock_live:
            mock_live.return_value.__enter__.return_value = MagicMock()
            run_watchable(args, render)

    assert render.call_count >= 1

def test_get_router_env_vars(monkeypatch):
    monkeypatch.setenv("KEENETIC_USER", "env_user")
    monkeypatch.setenv("KEENETIC_PASSWORD", "env_pass")
    monkeypatch.setenv("KEENETIC_PANEL", "http://env_panel")

    parser = build_parser()
    args   = parser.parse_args(["info"])

    with patch("KeeneticPy.CLI.Base.Keenetic") as mock_cls:
        get_router(args)
        mock_cls.assert_called_once_with(
            user     = "env_user",
            password = "env_pass",
            panel    = "http://env_panel",
            timeout  = 10.0
        )

def test_cmd_info_execution():
    parser = build_parser()
    args   = parser.parse_args(["info"])

    mock_router                              = MagicMock()
    mock_router.system.return_value          = {"uptime" : 120, "cpuload" : 5}
    mock_router.version.return_value         = {"model" : "Hero", "title" : "4.0", "device" : "TestDev"}
    mock_router.global_ip.return_value       = {"ipv4" : "1.2.3.4", "ipv6" : None}
    mock_router.internet_status.return_value = {"internet" : True, "gateway" : {"interface" : "PPPoE0"}}

    with patch("KeeneticPy.CLI.SystemCmds.get_router") as mock_get:
        mock_get.return_value.__enter__.return_value = mock_router
        cmd_info(args)
        mock_router.system.assert_called_once()
        mock_router.internet_status.assert_called_once()

def test_cmd_client_execution():
    parser      = build_parser()
    mock_router = MagicMock()

    with patch("KeeneticPy.CLI.NetworkCmds.get_router") as mock_get:
        mock_get.return_value.__enter__.return_value = mock_router

        with patch("KeeneticPy.CLI.NetworkCmds.set_speed_limit") as mock_limit:
            cmd_client(parser.parse_args(["client", "limit", "aa:bb:cc:dd:ee:ff", "--rx", "1000"]))
            mock_limit.assert_called_once()

        with patch("KeeneticPy.CLI.NetworkCmds.set_client_access") as mock_access:
            cmd_client(parser.parse_args(["client", "block", "aa:bb:cc:dd:ee:ff"]))
            mock_access.assert_called_once_with(mock_router, "aa:bb:cc:dd:ee:ff", permit=False)

        with patch("KeeneticPy.CLI.NetworkCmds.set_dhcp_binding") as mock_bind:
            cmd_client(parser.parse_args(["client", "bind", "aa:bb:cc:dd:ee:ff", "192.168.1.100"]))
            mock_bind.assert_called_once()

def test_cmd_modem_execution():
    parser      = build_parser()
    mock_router = MagicMock()

    with patch("KeeneticPy.CLI.NetworkCmds.get_router") as mock_get:
        mock_get.return_value.__enter__.return_value = mock_router

        with patch("KeeneticPy.CLI.NetworkCmds.get_modem_info") as mock_info:
            mock_info.return_value = {"operator" : "Turkcell", "technology" : "LTE"}
            cmd_modem(parser.parse_args(["modem", "status"]))
            mock_info.assert_called_once()

        with patch("KeeneticPy.CLI.NetworkCmds.get_sms_messages") as mock_sms:
            mock_sms.return_value = [{"phone" : "+90555", "text" : "Hi", "date" : "Today"}]
            cmd_modem(parser.parse_args(["modem", "sms-list"]))
            mock_sms.assert_called_once()

        with patch("KeeneticPy.CLI.NetworkCmds.send_sms") as mock_send:
            cmd_modem(parser.parse_args(["modem", "sms-send", "+90555", "Hi"]))
            mock_send.assert_called_once_with(mock_router, "+90555", "Hi")

        with patch("KeeneticPy.CLI.NetworkCmds.send_ussd") as mock_ussd:
            mock_ussd.return_value = "Balance OK"
            cmd_modem(parser.parse_args(["modem", "ussd", "*100#"]))
            mock_ussd.assert_called_once_with(mock_router, "*100#")

def test_cmd_system_and_route_execution():
    parser                                         = build_parser()
    mock_router                                    = MagicMock()
    mock_router.hosts.return_value                 = {"host" : []}
    mock_router.get_static_routes.return_value     = []
    mock_router.clean_multiple_routes.return_value = 0
    mock_router.backup.return_value                = "backup.zip"
    mock_router.reboot.return_value                = True
    mock_router.dsl_stats.return_value             = {"stat" : "ok"}
    mock_router.dsl_reset.return_value             = True

    with patch("KeeneticPy.CLI.SystemCmds.get_router") as mock_get_sys:
        mock_get_sys.return_value.__enter__.return_value = mock_router
        cmd_hosts(parser.parse_args(["hosts"]))
        cmd_backup(parser.parse_args(["backup"]))
        cmd_reboot(parser.parse_args(["reboot", "-y"]))
        cmd_dsl(parser.parse_args(["dsl", "stats"]))
        cmd_dsl(parser.parse_args(["dsl", "reset"]))

    with patch("KeeneticPy.CLI.NetworkCmds.get_router") as mock_get_net:
        mock_get_net.return_value.__enter__.return_value = mock_router
        cmd_route(parser.parse_args(["route", "list"]))
        cmd_route(parser.parse_args(["route", "clean"]))

def test_cmd_mesh_execution():
    parser                              = build_parser()
    mock_router                         = MagicMock()
    mock_router.mesh_nodes.return_value = [{
        "cid"                : "c1",
        "mac"                : "aa:bb:cc:dd:ee:ff",
        "known-host"         : "Extender",
        "ip"                 : "192.168.1.2",
        "mode"               : "extender",
        "fw"                 : "5.1.4",
        "internet-available" : True,
        "associations"       : 2,
        "system"             : {"cpuload" : 1, "memory" : "1000/2000", "uptime" : "100"},
        "rci"                : {"errors" : 0},
        "backhaul"           : {"speed" : "1000", "duplex" : "full"}
    }]

    with patch("KeeneticPy.CLI.SystemCmds.get_router") as mock_get:
        mock_get.return_value.__enter__.return_value = mock_router
        cmd_mesh(parser.parse_args(["mesh"]))
        mock_router.mesh_nodes.assert_called_once()

def test_cmd_mesh_no_nodes():
    parser                              = build_parser()
    mock_router                         = MagicMock()
    mock_router.mesh_nodes.return_value = []

    with patch("KeeneticPy.CLI.SystemCmds.get_router") as mock_get:
        mock_get.return_value.__enter__.return_value = mock_router
        cmd_mesh(parser.parse_args(["mesh"]))

def test_cli_parser_mesh_reboot():
    parser = build_parser()
    args   = parser.parse_args(["mesh", "reboot", "a4a2506e-4dae-11ed-9396-3be15a4fcdf3"])
    assert args.mesh_action == "reboot"
    assert args.cid         == "a4a2506e-4dae-11ed-9396-3be15a4fcdf3"

def test_cmd_mesh_reboot_execution():
    parser                                    = build_parser()
    mock_router                               = MagicMock()
    mock_router.reboot_mesh_node.return_value = True

    with patch("KeeneticPy.CLI.SystemCmds.get_router") as mock_get:
        mock_get.return_value.__enter__.return_value = mock_router
        cmd_mesh(parser.parse_args(["mesh", "reboot", "c1"]))
        mock_router.reboot_mesh_node.assert_called_once_with("c1")
        mock_router.mesh_nodes.assert_not_called()

def test_cmd_mesh_reboot_failure():
    parser                                    = build_parser()
    mock_router                               = MagicMock()
    mock_router.reboot_mesh_node.return_value = False

    with patch("KeeneticPy.CLI.SystemCmds.get_router") as mock_get:
        mock_get.return_value.__enter__.return_value = mock_router
        cmd_mesh(parser.parse_args(["mesh", "reboot", "c1"]))
