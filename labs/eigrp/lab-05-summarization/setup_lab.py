from netmiko import ConnectHandler
import os

# Active devices for lab-05: R1, R2, R3 (R4 enters at lab-06)
ROUTERS = [
    {"host": "127.0.0.1", "port": 5001, "device_type": "cisco_ios_telnet",
     "username": "", "password": "", "secret": "", "global_delay_factor": 2, "name": "R1"},
    {"host": "127.0.0.1", "port": 5002, "device_type": "cisco_ios_telnet",
     "username": "", "password": "", "secret": "", "global_delay_factor": 2, "name": "R2"},
    {"host": "127.0.0.1", "port": 5003, "device_type": "cisco_ios_telnet",
     "username": "", "password": "", "secret": "", "global_delay_factor": 2, "name": "R3"},
]

# Resolve initial-configs/ relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(SCRIPT_DIR, "initial-configs")


def load_config(device_name):
    # Read config, strip blank lines and comment lines starting with !
    config_path = os.path.join(CONFIG_DIR, f"{device_name}.cfg")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path, "r") as f:
        lines = [
            line.rstrip() for line in f
            if line.strip() and not line.strip().startswith("!")
        ]
    return lines


def push_config(router_info):
    name = router_info["name"]
    try:
        commands = load_config(name)
        # Build connection params without the custom 'name' key
        conn_params = {k: v for k, v in router_info.items() if k != "name"}
        print(f"  Connecting to {name} ({router_info['host']}:{router_info['port']})...")
        conn = ConnectHandler(**conn_params)
        conn.enable()
        conn.send_config_set(commands)
        conn.disconnect()
        print(f"  [OK] {name} configured successfully.")
    except Exception as e:
        print(f"  [FAIL] {name} — {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("=== ENARSI Lab 05: EIGRP Summarization ===")
    print("=" * 50)

    for router in ROUTERS:
        push_config(router)

    print()
    print("=" * 50)
    print("Setup complete. Suggested verification commands:")
    print("  show ip route eigrp")
    print("  show ip route | include Null0")
    print("  show ip eigrp topology")
    print("=" * 50)
