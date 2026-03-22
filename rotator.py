import time
import random
from manager import connect, disconnect
from utils import Colors

FAILED = {}

BLOCK_TIME = 600  


def is_blocked(config):
    return config in FAILED and time.time() < FAILED[config]


def mark_failed(config):
    FAILED[config] = time.time() + BLOCK_TIME


def rotate(configs, interval=60):
    try:
        print(f"\n{Colors.BLUE}[INFO]{Colors.RESET} Starting rotation...\n")

        last = None

        while True:
            available = [c for c in configs if not is_blocked(c)]

            if not available:
                print(f"{Colors.RED}[ERROR]{Colors.RESET} No available configs. Waiting...")
                time.sleep(10)
                continue
                
            choices = [c for c in available if c != last]
            if not choices:
                choices = available

            config = random.choice(choices)
            last = config

            print(f"{Colors.CYAN}[INFO]{Colors.RESET} Trying → {config}")

            ok = connect(config)

            if ok:
                print(f"\n{Colors.GREEN}[OK]{Colors.RESET} Rotation success\n")
                print(f"{Colors.BLUE}[INFO]{Colors.RESET} Next rotation in {interval}s...\n")

                for i in range(interval, 0, -1):
                    print(f"[TIMER] {i}s remaining.....", end="\r")
                    time.sleep(1)

                print(" " * 50, end="\r")

            else:
                print(f"{Colors.RED}[WARN]{Colors.RESET} Failed → {config}")
                mark_failed(config)

                print(f"{Colors.YELLOW}[INFO]{Colors.RESET} Trying another server immediately...\n")
                time.sleep(2)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[WARN]{Colors.RESET} Rotation stopped by user")
        disconnect()
