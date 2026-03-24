import os
import random
import time
import sys


class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    RESET = "\033[0m"


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "configs")


def logo():
    print(f"""
{Colors.MAGENTA}
=====================================================
||                                                 ||
||          ██╗   ██╗ ██████╗  ███╗   ██╗          ||
||          ██║   ██║ ██╔══██╗ ████╗  ██║          ||
||          ██║   ██║ ██████╔╝ ██╔██╗ ██║          ||
||          ╚██╗ ██╔╝ ██╔═══╝  ██║╚██╗██║          ||
||           ╚████╔╝  ██║      ██║ ╚████║          ||
||            ╚═══╝   ╚═╝      ╚═╝  ╚═══╝          ||
||                  VPN TOOL PRO                   ||
||                                      By: Dexlor ||
=====================================================
{Colors.RESET}
""")


def get_configs():
    if not os.path.exists(CONFIG_DIR):
        return []

    files = []
    for f in os.listdir(CONFIG_DIR):
        if f.endswith(".conf"):
            files.append(os.path.join("configs", f))
    return sorted(files)


def status_bar():
    states = ["🟩", "🟨", "🟥"]
    bar = "".join(random.choice(states) for _ in range(10))
    print(f"{Colors.CYAN}[STATUS]{Colors.RESET} {bar}")


def loading(text="Connecting", duration=2):
    print(f"{Colors.BLUE}{text}{Colors.RESET}", end="")
    for _ in range(duration * 5):
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(0.2)
    print()


def dashboard(ip="N/A", country="N/A", ks=False, status="CONNECTED"):
    ks_txt = "ON" if ks else "OFF"

    print(f"""
{Colors.MAGENTA}==== DASHBOARD ===={Colors.RESET}
{Colors.GREEN}Status:{Colors.RESET} {status}
{Colors.GREEN}IP:{Colors.RESET} {ip}
{Colors.YELLOW}Country:{Colors.RESET} {country}
{Colors.RED}KillSwitch:{Colors.RESET} {ks_txt}
""")