#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPECTED_DIR="/home/pi/NYC_METARMap"

if [[ "${EUID}" -ne 0 ]]; then
	echo "Run this installer with sudo:"
	echo "  sudo $0"
	exit 1
fi

if [[ "$APP_DIR" != "$EXPECTED_DIR" ]]; then
	echo "This appliance setup expects the repo at $EXPECTED_DIR"
	echo "Current path: $APP_DIR"
	echo
	echo "Move or clone it there, then run:"
	echo "  cd $EXPECTED_DIR"
	echo "  sudo ./install.sh"
	exit 1
fi

echo "Installing METARMap appliance setup..."

python3 "$APP_DIR/tools/validate_board_config.py"

apt-get update
apt-get install -y python3 python3-pip network-manager i2c-tools fonts-dejavu libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7
apt-get install -y libtiff6 || apt-get install -y libtiff5

python3 -m pip install --break-system-packages rpi_ws281x adafruit-circuitpython-neopixel adafruit-circuitpython-ssd1306 pillow astral \
	|| python3 -m pip install rpi_ws281x adafruit-circuitpython-neopixel adafruit-circuitpython-ssd1306 pillow astral

if command -v raspi-config >/dev/null 2>&1; then
	raspi-config nonint do_i2c 0 || true
fi

chmod +x "$APP_DIR/refresh.sh" "$APP_DIR/lightsoff.sh" "$APP_DIR/setup/metarmap-wifi-setup.py"

install -m 0644 "$APP_DIR/setup/metarmap.service" /etc/systemd/system/metarmap.service
install -m 0644 "$APP_DIR/setup/metarmap.timer" /etc/systemd/system/metarmap.timer
install -m 0644 "$APP_DIR/setup/metarmap-lights-off.service" /etc/systemd/system/metarmap-lights-off.service
install -m 0644 "$APP_DIR/setup/metarmap-lights-off.timer" /etc/systemd/system/metarmap-lights-off.timer
install -m 0644 "$APP_DIR/setup/metarmap-wifi-setup.service" /etc/systemd/system/metarmap-wifi-setup.service

systemctl enable --now NetworkManager.service
systemctl daemon-reload
systemctl enable --now metarmap-wifi-setup.service
systemctl enable --now metarmap.timer
systemctl enable --now metarmap-lights-off.timer

echo
echo "Done."
echo "If the Pi is not on Wi-Fi, join 'METARMap Setup' with password 'metarmap1'"
echo "Then open http://10.42.0.1:8080 and pick the home Wi-Fi network."
