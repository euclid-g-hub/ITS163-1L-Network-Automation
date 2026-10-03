import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ROUTER_IP = "127.0.0.1:8443"
USERNAME = "admin"
PASSWORD = "Cisco123!"
URL = f"https://{ROUTER_IP}/restconf/data/ietf-interfaces:interfaces"
HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}

try:
    response = requests.get(URL, auth=(USERNAME, PASSWORD), headers=HEADERS, verify=False, timeout=10)
    print(f"HTTP Status Code: {response.status_code}")

    if response.status_code == 200:
        interfaces = response.json()["ietf-interfaces:interfaces"]["interface"]
        print("\n" + "=" * 50)
        print(f"{'Interface Name':<30}{'Enabled':<10}")
        print("-" * 50)
        for intf in interfaces:
            print(f"{intf['name']:<30}{str(intf.get('enabled', 'N/A')):<10}")
        print("=" * 50)
    else:
        print(f"Request failed: {response.text}")

except requests.exceptions.ConnectionError:
    print(f"Connection failed: Unable to reach router at {ROUTER_IP}")
except requests.exceptions.Timeout:
    print(f"Connection failed: Request to {ROUTER_IP} timed out")
except requests.exceptions.RequestException as e:
    print(f"Connection failed: {e}")
