import random
import sys
from utils import get_configs, Colors, logo
from manager import (
    connect,
    disconnect,
    enable_kill_switch,
    disable_kill_switch,
    emergency_cleanup,
)
from rotator import rotate


def safe_exit():
    print(f"{Colors.GREEN}[OK]{Colors.RESET} Exiting...")
    sys.exit(0)


def print_configs(configs, label="config"):
    if not configs:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} No .config files found in configs/")
        return False

    for i, c in enumerate(configs):
        print(f"{Colors.YELLOW}{i}{Colors.RESET}: {c}")
    return True


def ask_index(configs, prompt_text):
    try:
        idx = int(input(prompt_text).strip())
    except ValueError:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Enter a valid number")
        return None

    if idx < 0 or idx >= len(configs):
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Invalid selection")
        return None

    return idx


# =========================
#  MENÚ PRINCIPAL
# =========================

def main_menu():
    logo()
    print(f"{Colors.GREEN}                >>>>> Mode of use <<<<<{Colors.RESET}")
    print(f"\n{Colors.GREEN}==========================================================={Colors.RESET}\n")
    print(f"{Colors.YELLOW}- Browse Mode → stable browsing (streaming / daily use){Colors.RESET}")
    print(f"{Colors.YELLOW}- Pentester Mode → rotation, anonymity and advanced control{Colors.RESET}\n")
    print(f"{Colors.GREEN}==========================================================={Colors.RESET}")

    print(f"{Colors.CYAN}1.{Colors.RESET} Browse Mode")
    print(f"{Colors.CYAN}2.{Colors.RESET} {Colors.BLUE}Pentester Mode{Colors.RESET}")
    print(f"{Colors.CYAN}5.{Colors.RESET}{Colors.RED} Exit{Colors.RESET}\n")


# =========================
#  BROWSE MODE
# =========================

def browse_banner():
    print(f"\n{Colors.MAGENTA}============================={Colors.RESET}")
    print(f"{Colors.MAGENTA}|          V P N            |{Colors.RESET}")
    print(f"{Colors.MAGENTA}|   B R O W S E - M O D E   |{Colors.RESET}")
    print(f"{Colors.MAGENTA}|       YOUR PRIVACY        |{Colors.RESET}")
    print(f"{Colors.MAGENTA}============================={Colors.RESET}\n")


def browse_mode():
    while True:
        browse_banner()
        print(f"{Colors.CYAN}1.{Colors.RESET} Show countries")
        print(f"{Colors.CYAN}2.{Colors.RESET} Connect")
        print(f"{Colors.CYAN}3.{Colors.RESET} Disconnect")
        print(f"{Colors.CYAN}4.{Colors.RESET} Back")
        print(f"{Colors.CYAN}5.{Colors.RESET}{Colors.RED} Exit{Colors.RESET}")

        choice = input("Select: ").strip()
        configs = get_configs()

        if choice == "1":
            print_configs(configs, "country")

        elif choice == "2":
            if not print_configs(configs, "country"):
                continue

            idx = ask_index(configs, "Select country: ")
            if idx is None:
                continue

            connect(configs[idx])

        elif choice == "3":
            disconnect()

        elif choice == "4":
            return

        elif choice == "5":
            safe_exit()

        else:
            print(f"{Colors.RED}[ERROR]{Colors.RESET} Invalid option")


# =========================
#  PENTESTER MODE
# =========================

def pentester_menu():
    print(f"\n{Colors.MAGENTA} ==================================={Colors.RESET}")
    print(f"{Colors.MAGENTA}||              V P N              ||{Colors.RESET}")
    print(f"{Colors.MAGENTA}||   P E N T E S T E R - M O D E   ||{Colors.RESET}")
    print(f"{Colors.MAGENTA}||            ANONYMOUS            ||{Colors.RESET}")
    print(f"{Colors.MAGENTA} ==================================={Colors.RESET}\n")
    print(f"{Colors.CYAN}1.{Colors.RESET} List configs")
    print(f"{Colors.CYAN}2.{Colors.RESET} Connect")
    print(f"{Colors.CYAN}3.{Colors.RESET} Disconnect")
    print(f"{Colors.CYAN}4.{Colors.RESET} Rotate IP")
    print(f"{Colors.CYAN}5.{Colors.RESET} Quick Connect (random)")
    print(f"{Colors.CYAN}6.{Colors.RESET} Enable Kill Switch")
    print(f"{Colors.CYAN}7.{Colors.RESET} Disable Kill Switch")
    print(f"{Colors.CYAN}8.{Colors.RESET} Emergency Cleanup")
    print(f"{Colors.CYAN}9.{Colors.RESET} Back")
    print(f"{Colors.CYAN}10.{Colors.RESET}{Colors.RED}Exit{Colors.RESET}")


def pentester_mode():
    while True:
        pentester_menu()
        choice = input("Select: ").strip()
        configs = get_configs()

        if choice == "1":
            print_configs(configs)

        elif choice == "2":
            if not print_configs(configs):
                continue

            idx = ask_index(configs, "Select config: ")
            if idx is None:
                continue

            connect(configs[idx])

        elif choice == "3":
            disconnect()

        elif choice == "4":
            if not configs:
                print(f"{Colors.RED}[ERROR]{Colors.RESET} No .config files found in configs/")
                continue

            try:
                interval = int(input("Seconds between rotation: ").strip())
            except ValueError:
                print(f"{Colors.RED}[ERROR]{Colors.RESET} Enter a valid number")
                continue

            if interval <= 0:
                print(f"{Colors.RED}[ERROR]{Colors.RESET} Interval must be greater than 0")
                continue

            rotate(configs, interval)

        elif choice == "5":
            if not configs:
                print(f"{Colors.RED}[ERROR]{Colors.RESET} No .config files found in configs/")
                continue

            config = random.choice(configs)
            print(f"{Colors.BLUE}[INFO]{Colors.RESET} Random config selected: {config}")
            connect(config)

        elif choice == "6":
            enable_kill_switch()

        elif choice == "7":
            disable_kill_switch()

        elif choice == "8":
            emergency_cleanup()

        elif choice == "9":
            return

        elif choice == "10":
            safe_exit()

        else:
            print(f"{Colors.RED}[ERROR]{Colors.RESET} Invalid option")


# =========================
#  ENTRY POINT
# =========================

def main():
    while True:
        main_menu()
        choice = input("Select an option (1, 2 or 3): ").strip()

        if choice == "1":
            browse_mode()

        elif choice == "2":
            pentester_mode()

        elif choice == "3":
            safe_exit()

        else:
            print(f"{Colors.RED}[ERROR]{Colors.RESET} Invalid option")


if __name__ == "__main__":
    main()
