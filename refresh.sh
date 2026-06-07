#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_DIR="/run/metarmap"
NOW_HHMM="$(date +%H%M)"

/usr/bin/sudo /usr/bin/install -d -m 755 "$RUN_DIR"
/usr/bin/sudo pkill -F "$RUN_DIR/offpid.pid" 2>/dev/null || true
/usr/bin/sudo pkill -F "$RUN_DIR/metarpid.pid" 2>/dev/null || true

if (( 10#$NOW_HHMM < 700 )); then
	echo "Map is in overnight lights-off window; LEDs remain off until 07:00."
	/usr/bin/sudo /usr/bin/python3 "$APP_DIR/pixelsoff.py"
	exit 0
fi

/usr/bin/sudo /usr/bin/python3 "$APP_DIR/metar.py"
