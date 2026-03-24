import os
import time
import subprocess
import requests
from utils import Colors, loading, status_bar, dashboard

CURRENT_INTERFACE = None

KNOWN_INTERFACES = ["proton", "ca", "jp", "mx", "nl1", "nl2", "no", "sg"]


def get_interface_name(config_path):
    return os.path.splitext(os.path.basename(config_path))[0]


def is_interface_up(interface_name=None):
    target = interface_name if interface_name else CURRENT_INTERFACE
    if not target:
        return False

    result = subprocess.run(
        ["ip", "a"],
        capture_output=True,
        text=True
    )
    return f"{target}:" in result.stdout


def get_ip(timeout=4):
    try:
        return requests.get("https://ifconfig.me", timeout=timeout).text.strip()
    except Exception:
        return None


def get_geo(timeout=4):
    try:
        data = requests.get("http://ip-api.com/json/", timeout=timeout).json()
        return data.get("country", "Unknown")
    except Exception:
        return "Unknown"


def get_flag(country):
    flags = {
        "Canada": "🇨🇦",
        "Netherlands": "🇳🇱",
        "United States": "🇺🇸",
        "Japan": "🇯🇵",
        "Singapore": "🇸🇬",
        "Mexico": "🇲🇽",
        "Norway": "🇳🇴",
    }
    return flags.get(country, "")


def is_kill_switch_enabled():
    result = subprocess.run(
        ["sudo", "iptables", "-S"],
        capture_output=True,
        text=True
    )
    return "-A OUTPUT -j DROP" in result.stdout


def enable_kill_switch():
    global CURRENT_INTERFACE

    if is_kill_switch_enabled():
        print(f"{Colors.YELLOW}[WARN]{Colors.RESET} Kill switch already enabled")
        return

    if not CURRENT_INTERFACE:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} No active VPN interface for kill switch")
        return

    print(f"{Colors.YELLOW}[INFO]{Colors.RESET} Enabling kill switch...")

    commands = [
        ["sudo", "iptables", "-I", "OUTPUT", "1", "-o", "lo", "-j", "ACCEPT"],
        ["sudo", "iptables", "-I", "OUTPUT", "2", "-o", CURRENT_INTERFACE, "-j", "ACCEPT"],
        ["sudo", "iptables", "-I", "OUTPUT", "3", "-m", "conntrack", "--ctstate", "ESTABLISHED,RELATED", "-j", "ACCEPT"],
        ["sudo", "iptables", "-A", "OUTPUT", "-j", "DROP"],
    ]

    for cmd in commands:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"{Colors.GREEN}[OK]{Colors.RESET} Kill switch enabled")


def disable_kill_switch():
    print(f"{Colors.MAGENTA}[INFO]{Colors.RESET} Disabling kill switch...")

    commands = [
        ["sudo", "iptables", "-D", "OUTPUT", "-j", "DROP"],
        ["sudo", "iptables", "-D", "OUTPUT", "-m", "conntrack", "--ctstate", "ESTABLISHED,RELATED", "-j", "ACCEPT"],
    ]

    for cmd in commands:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for iface in ["lo"] + KNOWN_INTERFACES:
        subprocess.run(
            ["sudo", "iptables", "-D", "OUTPUT", "-o", iface, "-j", "ACCEPT"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    print(f"{Colors.GREEN}[OK]{Colors.RESET} Kill switch disabled")


def wait_for_tunnel_ready(interface_name, max_wait=15):
    """
    Espera hasta que:
    1. La interfaz exista
    2. Haya salida real a internet
    3. Se pueda obtener IP pública
    """
    start = time.time()

    while time.time() - start < max_wait:
        if not is_interface_up(interface_name):
            time.sleep(1)
            continue

        ip = get_ip(timeout=3)
        if ip:
            return True, ip

        time.sleep(1)

    return False, None


def cleanup_interface(interface_name):
    subprocess.run(
        ["sudo", "ip", "link", "delete", interface_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def emergency_cleanup():
    global CURRENT_INTERFACE

    print(f"{Colors.YELLOW}[INFO]{Colors.RESET} Running emergency cleanup...")

    for iface in KNOWN_INTERFACES:
        subprocess.run(
            ["sudo", "ip", "link", "delete", iface],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    for iface in KNOWN_INTERFACES:
        subprocess.run(
            ["sudo", "resolvconf", "-d", iface, "-f"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    disable_kill_switch()
    CURRENT_INTERFACE = None

    print(f"{Colors.GREEN}[OK]{Colors.RESET} Cleanup complete")


def connect(config_path):
    global CURRENT_INTERFACE

    interface_name = get_interface_name(config_path)
    name = os.path.basename(config_path)

    print(f"{Colors.BLUE}[INFO]{Colors.RESET} Connecting → {name}")

    ks_active = is_kill_switch_enabled()
    if ks_active:
        print(f"{Colors.YELLOW}[INFO]{Colors.RESET} Temporarily disabling kill switch for reconnect...")
        disable_kill_switch()

    loading("Connecting to VPN")

    if CURRENT_INTERFACE and is_interface_up(CURRENT_INTERFACE):
        print(f"{Colors.YELLOW}[INFO]{Colors.RESET} Cleaning previous interface: {CURRENT_INTERFACE}")
        cleanup_interface(CURRENT_INTERFACE)

    if is_interface_up(interface_name):
        print(f"{Colors.YELLOW}[INFO]{Colors.RESET} Interface already exists. Cleaning...")
        cleanup_interface(interface_name)

    result = subprocess.run(
        ["sudo", "wg-quick", "up", config_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if result.returncode != 0:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Failed to bring tunnel up")
        emergency_cleanup()
        return False

    CURRENT_INTERFACE = interface_name
    print(f"{Colors.CYAN}[INFO]{Colors.RESET} Tunnel up. Waiting for public connectivity...")

    ready, ip = wait_for_tunnel_ready(interface_name, max_wait=15)

    if not ready:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Tunnel created but public connectivity not ready")
        emergency_cleanup()
        return False

    country = get_geo(timeout=4)
    flag = get_flag(country)

    if ks_active:
        enable_kill_switch()

    print(f"{Colors.GREEN}[OK]{Colors.RESET} Connected")
    print(f"    IP: {ip}")
    print(f"    Location: {flag} {country}")

    status_bar()
    dashboard(ip, country, ks=is_kill_switch_enabled(), status="CONNECTED")
    return True


def disconnect():
    global CURRENT_INTERFACE

    if not CURRENT_INTERFACE:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} No active interface tracked")
        return

    if is_kill_switch_enabled():
        print(f"{Colors.RED}[WARN]{Colors.RESET} Kill switch is ON → You may lose connectivity")

    print(f"{Colors.MAGENTA}[INFO]{Colors.RESET} Disconnecting {CURRENT_INTERFACE}...")
    cleanup_interface(CURRENT_INTERFACE)
    print(f"{Colors.GREEN}[OK]{Colors.RESET} Disconnected")

    CURRENT_INTERFACE = None