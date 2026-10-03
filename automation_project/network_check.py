import json
import platform
import subprocess
from datetime import datetime

INVENTORY_FILE = "inventory.json"
OUTPUT_FILE = "output.json"

def load_inventory():
    try:
        with open(INVENTORY_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {INVENTORY_FILE} not found")
        return []
    except json.JSONDecodeError:
        print(f"Error: {INVENTORY_FILE} is not valid JSON")
        return []

def check_device(ip):
    flag = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        result = subprocess.run(["ping", flag, "1", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
        return "UP" if result.returncode == 0 else "DOWN"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "DOWN"

def save_results(results):
    try:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(results, f, indent=4)
        print(f"\nResults saved to {OUTPUT_FILE}")
    except OSError as e:
        print(f"Error saving results: {e}")

def main():
    devices = load_inventory()
    if not devices:
        print("No devices to check.")
        return

    results = []
    print("=" * 70)
    print(f"{'Hostname':<14}{'IP Address':<17}{'Location':<15}{'Status':<8}")
    print("-" * 70)

    for d in devices:
        try:
            status = check_device(d["ip"])
            print(f"{d['hostname']:<14}{d['ip']:<17}{d['location']:<15}{status:<8}")
            results.append({
                "hostname": d["hostname"],
                "ip": d["ip"],
                "type": d["type"],
                "location": d["location"],
                "status": status,
                "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        except KeyError as e:
            print(f"Error: device entry missing field {e}")

    print("=" * 70)
    up = sum(1 for r in results if r["status"] == "UP")
    print(f"UP: {up}   DOWN: {len(results) - up}   TOTAL: {len(results)}")
    save_results(results)

if __name__ == "__main__":
    main()
