import base64
import json
import os
import ssl
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORT = 8443
USERNAME = "admin"
PASSWORD = "Cisco123!"
BASE = "/restconf/data/ietf-interfaces:interfaces"
HERE = os.path.dirname(os.path.abspath(__file__))

interfaces = {
    "GigabitEthernet1": {
        "name": "GigabitEthernet1",
        "description": "MANAGEMENT",
        "type": "iana-if-type:ethernetCsmacd",
        "enabled": True,
        "ietf-ip:ipv4": {"address": [{"ip": "192.168.10.1", "netmask": "255.255.255.0"}]},
    },
    "GigabitEthernet2": {
        "name": "GigabitEthernet2",
        "description": "LAN",
        "type": "iana-if-type:ethernetCsmacd",
        "enabled": True,
        "ietf-ip:ipv4": {"address": [{"ip": "10.10.10.1", "netmask": "255.255.255.0"}]},
    },
    "GigabitEthernet3": {
        "name": "GigabitEthernet3",
        "type": "iana-if-type:ethernetCsmacd",
        "enabled": False,
        "ietf-ip:ipv4": {},
    },
}


def restconf_error(tag, message):
    return {"ietf-restconf:errors": {"error": [{"error-type": "application", "error-tag": tag, "error-message": message}]}}


class RestconfHandler(BaseHTTPRequestHandler):
    server_version = "nginx"
    sys_version = ""

    def log_message(self, fmt, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {self.client_address[0]} {fmt % args}")

    def send_json(self, code, body=None):
        data = json.dumps(body, indent=2).encode() if body is not None else b""
        self.send_response(code)
        self.send_header("Content-Type", "application/yang-data+json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if data:
            self.wfile.write(data)

    def authorized(self):
        header = self.headers.get("Authorization", "")
        if not header.startswith("Basic "):
            return False
        try:
            user, pwd = base64.b64decode(header[6:]).decode().split(":", 1)
        except Exception:
            return False
        return user == USERNAME and pwd == PASSWORD

    def check_auth(self):
        if self.authorized():
            return True
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="restconf"')
        self.send_header("Content-Length", "0")
        self.end_headers()
        return False

    def interface_name(self):
        prefix = BASE + "/interface="
        if self.path.startswith(prefix):
            return self.path[len(prefix):].split("?")[0]
        return None

    def do_GET(self):
        if not self.check_auth():
            return
        path = self.path.split("?")[0]
        if path == BASE:
            self.send_json(200, {"ietf-interfaces:interfaces": {"interface": list(interfaces.values())}})
            return
        name = self.interface_name()
        if name in interfaces:
            self.send_json(200, {"ietf-interfaces:interface": interfaces[name]})
        elif name:
            self.send_json(404, restconf_error("invalid-value", "uri keypath not found"))
        else:
            self.send_json(404, restconf_error("invalid-value", "uri keypath not found"))

    def do_PUT(self):
        if not self.check_auth():
            return
        name = self.interface_name()
        if not name:
            self.send_json(405, restconf_error("operation-not-supported", "PUT is only supported on an interface"))
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            intf = body["ietf-interfaces:interface"]
        except (ValueError, KeyError):
            self.send_json(400, restconf_error("malformed-message", "invalid JSON payload"))
            return
        if intf.get("name") != name:
            self.send_json(400, restconf_error("invalid-value", "interface name in body does not match the URL"))
            return
        existed = name in interfaces
        interfaces[name] = intf
        self.send_json(204 if existed else 201)


def main():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(os.path.join(HERE, "cert.pem"), os.path.join(HERE, "key.pem"))
    server = ThreadingHTTPServer((HOST, PORT), RestconfHandler)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    print(f"Mock IOS XE RESTCONF server running on https://{HOST}:{PORT}")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")


if __name__ == "__main__":
    main()
