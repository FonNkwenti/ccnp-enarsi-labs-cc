"""
Lab 02 — Fault Scenario 01
Fault: R2 IPv4 address-family configured with wrong autonomous-system number (200 vs 100).
Effect: R2 loses IPv4 EIGRP adjacency with R1 and R3; IPv4 routes disappear from R2.
       IPv6 adjacency is unaffected (separate AF with correct AS).

Symptom presented to student:
  "R2 shows no IPv4 EIGRP neighbors. The IPv6 EIGRP table is intact but
   the IPv4 routing table has no EIGRP entries."
"""

from netmiko import ConnectHandler

R2 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5002,
    "username": "",
    "password": "",
    "secret": "",
    "global_delay_factor": 2,
}

# Inject: replace IPv4 AF autonomous-system with AS 200
fault_commands = [
    "router eigrp ENARSI",
    "address-family ipv4 unicast autonomous-system 200",
    "exit-address-family",
    # Remove the correct AS 100 block
    "no address-family ipv4 unicast autonomous-system 100",
]


def main():
    print("[*] Injecting Scenario 01 — IPv4 AF AS mismatch on R2 (AS 200 instead of 100)...")
    with ConnectHandler(**R2) as net_connect:
        net_connect.enable()
        net_connect.send_config_set(fault_commands, cmd_verify=False)
    print("[+] Fault injected. R2 IPv4 EIGRP adjacency will drop within ~15 seconds.")
    print("    Verify: show ip eigrp neighbors  (expect: empty on R2)")


if __name__ == "__main__":
    main()
