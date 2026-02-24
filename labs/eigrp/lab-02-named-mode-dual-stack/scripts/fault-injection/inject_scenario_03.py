"""
Lab 02 — Fault Scenario 03
Fault: 'network 10.0.0.3 0.0.0.0' removed from R3's IPv4 address-family.
Effect: R3's Loopback0 (10.0.0.3/32) is not advertised to EIGRP neighbors.
       R1 and R2 lose the route to 10.0.0.3/32 in their IPv4 EIGRP table.
       All three IPv4 adjacencies remain up; only the loopback prefix disappears.

Symptom presented to student:
  "Ping from R1 to 10.0.0.3 fails. All three EIGRP IPv4 adjacencies are up
   and all link subnets are present in the routing table, but 10.0.0.3 is missing."
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

# Inject: remove Loopback0 network statement from R3 IPv4 AF
fault_commands = [
    "router eigrp ENARSI",
    "address-family ipv4 unicast autonomous-system 100",
    "no network 10.0.0.3 0.0.0.0",
    "exit-address-family",
]


def main():
    print("[*] Injecting Scenario 03 — Missing Lo0 network statement on R3 IPv4 AF...")
    with ConnectHandler(**R3) as net_connect:
        net_connect.enable()
        net_connect.send_config_set(fault_commands, cmd_verify=False)
    print("[+] Fault injected. 10.0.0.3/32 will disappear from R1/R2 routing tables.")
    print("    Verify: show ip route eigrp  (on R1 — expect no 10.0.0.3 entry)")


if __name__ == "__main__":
    main()
