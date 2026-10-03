import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ROUTER_IP = "127.0.0.1:8443"
USERNAME = "admin"
PASSWORD = "Cisco123!"
INTERFACE = "Loopback100"
URL = f"https://{ROUTER_IP}/restconf/data/ietf-interfaces:interfaces/interface={INTERFACE}"
HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}

payload = {
    "ietf-interfaces:interface": {
        "name": INTERFACE,
        "description": "STUDENT-AUTOMATION",
        "type": "iana-if-type:softwareLoopback",
        "enabled": True,
        "ietf-ip:ipv4": {
            "address": [
                {
                    "ip": "10.100.100.1",
                    "netmask": "255.255.255.255"
                }
            ]
        }
    }
}

try:
    response = requests.put(URL, auth=(USERNAME, PASSWORD), headers=HEADERS, json=payload, verify=False, timeout=10)
    print(f"PUT Status Code: {response.status_code}")

    if response.status_code in (200, 201, 204):
        print(f"Configuration of {INTERFACE} SUCCEEDED")
    else:
        print(f"Configuration of {INTERFACE} FAILED: {response.text}")

    verify = requests.get(URL, auth=(USERNAME, PASSWORD), headers=HEADERS, verify=False, timeout=10)
    print(f"\nGET Status Code: {verify.status_code}")

    if verify.status_code == 200:
        intf = verify.json()["ietf-interfaces:interface"]
        if isinstance(intf, list):
            intf = intf[0]
        addr = intf.get("ietf-ip:ipv4", {}).get("address", [{}])[0]
        print("=" * 45)
        print(f"Interface   : {intf['name']}")
        print(f"Description : {intf.get('description')}")
        print(f"IP Address  : {addr.get('ip')}")
        print(f"Subnet Mask : {addr.get('netmask')}")
        print(f"Enabled     : {intf.get('enabled')}")
        print("=" * 45)
    else:
        print(f"Verification FAILED: {verify.text}")

except requests.exceptions.ConnectionError:
    print(f"Connection failed: Unable to reach router at {ROUTER_IP}")
except requests.exceptions.Timeout:
    print(f"Connection failed: Request to {ROUTER_IP} timed out")
except requests.exceptions.RequestException as e:
    print(f"Connection failed: {e}")
