"""
Lab 02 — Fault Scenario 02
Fault: 'ipv6 unicast-routing' removed from R3.
Effect: R3 stops forwarding IPv6 traffic and its IPv6 EIGRP AF becomes inactive.
       R3 drops IPv6 EIGRP adjacency with R1 and R2.
       IPv4 EIGRP adjacency and IPv4 routing remain fully operational.

Symptom presented to student:
  "R3 IPv6 EIGRP neighbor table is empty. Pings to R3 IPv6 addresses fail
   from R1 and R2, but IPv4 pings succeed and IPv4 EIGRP is fully operational."
"""

from netmiko import ConnectHandler

R3 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5003,
    "username": "",
    "password": "",
    "secret": "",
    "global_delay_factor": 2,
}

# Inject: disable IPv6 unicast routing on R3
fault_commands = [
    "no ipv6 unicast-routing",
]


def main():
    print("[*] Injecting Scenario 02 — 'no ipv6 unicast-routing' on R3...")
    with ConnectHandler(**R3) as net_connect:
        net_connect.enable()
        net_connect.send_config_set(fault_commands, cmd_verify=False)
    print("[+] Fault injected. R3 IPv6 EIGRP adjacency will drop within ~15 seconds.")
    print("    Verify: show ipv6 eigrp neighbors  (expect: empty on R1/R2)")


if __name__ == "__main__":
    main()
