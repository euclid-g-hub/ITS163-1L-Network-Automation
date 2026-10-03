devices = [
    {"hostname": "R1-CORE", "ip": "192.168.10.1", "type": "Cisco ISR 4331 Router", "location": "Main Office", "status": "up"},
    {"hostname": "SW1-ACCESS", "ip": "192.168.10.2", "type": "Cisco Catalyst 2960 Switch", "location": "Floor 1", "status": "up"},
    {"hostname": "SW2-DIST", "ip": "192.168.10.3", "type": "Cisco Catalyst 3650 Switch", "location": "Floor 2", "status": "down"},
    {"hostname": "FW1-EDGE", "ip": "192.168.10.4", "type": "Cisco ASA 5506-X Firewall", "location": "Data Center", "status": "up"},
]

def print_header(title):
    print("\n" + "=" * 95)
    print(title)
    print("=" * 95)
    print(f"{'Hostname':<14}{'Management IP':<17}{'Device Type':<30}{'Location':<15}{'Status':<8}")
    print("-" * 95)

def print_device(d):
    print(f"{d['hostname']:<14}{d['ip']:<17}{d['type']:<30}{d['location']:<15}{d['status'].upper():<8}")

print_header("ALL NETWORK DEVICES")
for d in devices:
    print_device(d)

print_header("DEVICES WITH STATUS UP")
for d in devices:
    if d["status"] == "up":
        print_device(d)

up_count = sum(1 for d in devices if d["status"] == "up")
print("\n" + "=" * 95)
print(f"Operational devices: {up_count} of {len(devices)}")
print("=" * 95)
