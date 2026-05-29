#!/usr/bin/env python3

import html
import subprocess
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


SETUP_SSID = "METARMap Setup"
SETUP_PASSWORD = "metarmap1"
SETUP_CONNECTION = "metarmap-setup"
PORT = 8080


def run(args, check=False):
	result = subprocess.run(args, text=True, capture_output=True)
	if check and result.returncode != 0:
		raise RuntimeError(result.stderr.strip() or result.stdout.strip())
	return result


def wifi_interface():
	result = run(["nmcli", "-t", "-f", "DEVICE,TYPE", "device", "status"])
	for line in result.stdout.splitlines():
		parts = line.split(":")
		if len(parts) >= 2 and parts[1] == "wifi":
			return parts[0]
	return "wlan0"


def active_wifi_ssid():
	result = run(["nmcli", "-t", "-f", "ACTIVE,SSID", "device", "wifi"])
	for line in result.stdout.splitlines():
		if line.startswith("yes:"):
			return line.split(":", 1)[1]
	return ""


def ensure_setup_hotspot():
	ssid = active_wifi_ssid()
	if ssid:
		return

	iface = wifi_interface()
	run(["nmcli", "connection", "down", SETUP_CONNECTION])
	run(["nmcli", "connection", "delete", SETUP_CONNECTION])
	run([
		"nmcli",
		"device",
		"wifi",
		"hotspot",
		"ifname",
		iface,
		"con-name",
		SETUP_CONNECTION,
		"ssid",
		SETUP_SSID,
		"password",
		SETUP_PASSWORD,
	], check=True)


def scan_networks():
	iface = wifi_interface()
	run(["nmcli", "device", "wifi", "rescan", "ifname", iface])
	result = run(["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "device", "wifi", "list", "ifname", iface])
	seen = set()
	networks = []
	for line in result.stdout.splitlines():
		parts = line.split(":")
		ssid = parts[0].replace("\\:", ":").strip()
		if not ssid or ssid in seen or ssid == SETUP_SSID:
			continue
		seen.add(ssid)
		signal = parts[1] if len(parts) > 1 else ""
		security = parts[2] if len(parts) > 2 else ""
		networks.append({"ssid": ssid, "signal": signal, "security": security})
	return networks


def connect_to_wifi(ssid, password):
	time.sleep(2)
	iface = wifi_interface()
	run(["nmcli", "connection", "down", SETUP_CONNECTION])

	args = ["nmcli", "device", "wifi", "connect", ssid, "ifname", iface]
	if password:
		args.extend(["password", password])

	result = run(args)
	if result.returncode != 0:
		time.sleep(5)
		ensure_setup_hotspot()
		return

	time.sleep(5)
	run(["systemctl", "restart", "metarmap.service"])


class WifiSetupHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path.startswith("/health"):
			self.send_response(200)
			self.end_headers()
			self.wfile.write(b"ok")
			return

		self.render_page()

	def do_POST(self):
		if self.path != "/save":
			self.send_error(404)
			return

		length = int(self.headers.get("Content-Length", "0"))
		body = self.rfile.read(length).decode("utf-8")
		form = urllib.parse.parse_qs(body)
		ssid = form.get("ssid", [""])[0].strip()
		password = form.get("password", [""])[0]

		if not ssid:
			self.render_page("Choose a Wi-Fi network first.")
			return

		threading.Thread(target=connect_to_wifi, args=(ssid, password), daemon=True).start()
		self.render_connecting(ssid)

	def log_message(self, fmt, *args):
		print("%s - %s" % (self.address_string(), fmt % args))

	def render_page(self, message=""):
		ssid = active_wifi_ssid()
		status = "Connected to " + ssid if ssid and ssid != SETUP_SSID else "Setup mode is active"
		try:
			networks = scan_networks()
			network_options = "\n".join(
				'<option value="{ssid}" label="{ssid} ({signal}%{secured})"></option>'.format(
					ssid=html.escape(net["ssid"], quote=True),
					signal=html.escape(net["signal"]),
					secured=", locked" if net["security"] else "",
				)
				for net in networks
			)
		except Exception as exc:
			network_options = ""
			message = "Could not scan networks yet. Refresh in a minute. " + str(exc)

		body = """<!doctype html>
<html lang="en">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>METARMap Wi-Fi Setup</title>
<style>
body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f6f7f9; color: #17202a; }}
main {{ max-width: 520px; margin: 0 auto; padding: 32px 20px; }}
h1 {{ font-size: 30px; margin: 0 0 8px; }}
p {{ line-height: 1.45; }}
.panel {{ background: #fff; border: 1px solid #d9dee6; border-radius: 8px; padding: 20px; box-shadow: 0 8px 28px rgba(20, 32, 50, 0.08); }}
label {{ display: block; font-weight: 650; margin-top: 16px; }}
select, input {{ width: 100%; box-sizing: border-box; font-size: 18px; padding: 12px; margin-top: 6px; border: 1px solid #b9c1cc; border-radius: 6px; }}
button {{ width: 100%; margin-top: 20px; border: 0; border-radius: 6px; padding: 14px 18px; background: #1264a3; color: white; font-weight: 750; font-size: 18px; }}
.status {{ font-weight: 700; color: #1264a3; }}
.message {{ color: #9a3412; font-weight: 650; }}
.hint {{ color: #5d6876; font-size: 14px; }}
</style>
</head>
<body>
<main>
<h1>METARMap Wi-Fi</h1>
<p class="status">{status}</p>
<div class="panel">
{message}
<form method="post" action="/save">
<label for="ssid">Home Wi-Fi</label>
<input id="ssid" name="ssid" list="networks" required placeholder="Choose or type a network name" autocomplete="off">
<datalist id="networks">
{network_options}
</datalist>
<label for="password">Wi-Fi Password</label>
<input id="password" name="password" type="password" autocomplete="current-password">
<button type="submit">Connect Map</button>
</form>
<p class="hint">Setup network: {setup_ssid}. Password: {setup_password}. This page is at http://10.42.0.1:8080.</p>
</div>
</main>
</body>
</html>""".format(
			status=html.escape(status),
			message='<p class="message">' + html.escape(message) + "</p>" if message else "",
			network_options=network_options,
			setup_ssid=html.escape(SETUP_SSID),
			setup_password=html.escape(SETUP_PASSWORD),
		)
		self.send_html(body)

	def render_connecting(self, ssid):
		body = """<!doctype html>
<html lang="en">
<head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Connecting METARMap</title></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:520px;margin:40px auto;padding:0 20px;line-height:1.45">
<h1>Connecting...</h1>
<p>The map is trying to join <strong>{ssid}</strong>. The setup Wi-Fi may disappear now.</p>
<p>If the map does not light up after two minutes, reconnect to <strong>{setup_ssid}</strong> and try the password again.</p>
</body>
</html>""".format(ssid=html.escape(ssid), setup_ssid=html.escape(SETUP_SSID))
		self.send_html(body)

	def send_html(self, body):
		encoded = body.encode("utf-8")
		self.send_response(200)
		self.send_header("Content-Type", "text/html; charset=utf-8")
		self.send_header("Content-Length", str(len(encoded)))
		self.end_headers()
		self.wfile.write(encoded)


def hotspot_watchdog():
	while True:
		try:
			ensure_setup_hotspot()
		except Exception as exc:
			print("Wi-Fi setup watchdog error: " + str(exc))
		time.sleep(30)


if __name__ == "__main__":
	threading.Thread(target=hotspot_watchdog, daemon=True).start()
	server = ThreadingHTTPServer(("0.0.0.0", PORT), WifiSetupHandler)
	print("METARMap Wi-Fi setup server running on port " + str(PORT))
	server.serve_forever()
