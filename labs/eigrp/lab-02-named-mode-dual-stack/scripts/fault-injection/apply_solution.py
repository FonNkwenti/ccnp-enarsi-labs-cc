"""
Lab 02 — Apply Solution
Restores all three routers to the correct named-mode dual-stack EIGRP state.
Idempotent — safe to run regardless of which scenario was injected.

Remediation actions:
  R1: Ensure named mode EIGRP ENARSI, IPv4 AF AS 100, IPv6 AF AS 100
  R2: Ensure named mode EIGRP ENARSI, IPv4 AF AS 100, IPv6 AF AS 100
  R3: Restore ipv6 unicast-routing, ensure named mode with all network statements
"""

from netmiko import ConnectHandler

devices = [
    {
        "name": "R1",
        "host": "127.0.0.1",
        "port": 5001,
        "username": "",
        "password": "",
        "secret": "",
        "device_type": "cisco_ios_telnet",
        "global_delay_factor": 2,
        "commands": [
            # Remove any stale classic EIGRP if present
            "no router eigrp 100",
            # Rebuild named mode
            "router eigrp ENARSI",
            "address-family ipv4 unicast autonomous-system 100",
            "eigrp log-neighbor-changes",
            "network 10.12.0.0 0.0.0.3",
            "network 10.13.0.0 0.0.0.3",
            "network 10.0.0.1 0.0.0.0",
            "eigrp router-id 10.0.0.1",
            "no auto-summary",
            "exit-address-family",
            "address-family ipv6 unicast autonomous-system 100",
            "eigrp log-neighbor-changes",
            "eigrp router-id 10.0.0.1",
            "exit-address-family",
        ],
    },
    {
        "name": "R2",
        "host": "127.0.0.1",
        "port": 5002,
        "username": "",
        "password": "",
        "secret": "",
        "device_type": "cisco_ios_telnet",
        "global_delay_factor": 2,
        "commands": [
            # Remove wrong AS 200 block if scenario 01 was injected
            "router eigrp ENARSI",
            "no address-family ipv4 unicast autonomous-system 200",
            # Rebuild correct IPv4 AF
            "address-family ipv4 unicast autonomous-system 100",
            "eigrp log-neighbor-changes",
            "network 10.12.0.0 0.0.0.3",
            "network 10.23.0.0 0.0.0.3",
            "network 10.0.0.2 0.0.0.0",
            "eigrp router-id 10.0.0.2",
            "no auto-summary",
            "exit-address-family",
            "address-family ipv6 unicast autonomous-system 100",
            "eigrp log-neighbor-changes",
            "eigrp router-id 10.0.0.2",
            "exit-address-family",
        ],
    },
    {
        "name": "R3",
        "host": "127.0.0.1",
        "port": 5003,
        "username": "",
        "password": "",
        "secret": "",
        "device_type": "cisco_ios_telnet",
        "global_delay_factor": 2,
        "commands": [
            # Restore ipv6 unicast-routing (scenario 02 removes it)
            "ipv6 unicast-routing",
            # Rebuild named mode with Lo0 network statement (scenario 03 removes it)
            "router eigrp ENARSI",
            "address-family ipv4 unicast autonomous-system 100",
            "eigrp log-neighbor-changes",
            "network 10.13.0.0 0.0.0.3",
            "network 10.23.0.0 0.0.0.3",
            "network 10.0.0.3 0.0.0.0",
            "eigrp router-id 10.0.0.3",
            "no auto-summary",
            "exit-address-family",
            "address-family ipv6 unicast autonomous-system 100",
            "eigrp log-neighbor-changes",
            "eigrp router-id 10.0.0.3",
            "exit-address-family",
        ],
    },
]


def restore_device(device):
    conn_params = {k: v for k, v in device.items() if k not in ("name", "commands")}
    print(f"[*] Restoring {device['name']} ({device['host']}:{device['port']})...")
    with ConnectHandler(**conn_params) as net_connect:
        net_connect.enable()
        net_connect.send_config_set(device["commands"], cmd_verify=False)
        net_connect.send_command("write memory", expect_string=r"#")
    print(f"[+] {device['name']} — restored and saved.")


def main():
    print("=" * 55)
    print("Lab 02 Apply Solution — Restoring named-mode dual-stack EIGRP")
    print("=" * 55)
    for device in devices:
        try:
            restore_device(device)
        except Exception as exc:
            print(f"[!] {device['name']} failed: {exc}")
    print("\n[*] Solution applied. Verify with:")
    print("    show ip eigrp neighbors")
    print("    show ipv6 eigrp neighbors")
    print("    show ip route eigrp")
    print("    show ipv6 route eigrp")


if __name__ == "__main__":
    main()
