#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_DIR="/run/metarmap"

/usr/bin/sudo /usr/bin/install -d -m 755 "$RUN_DIR"
/usr/bin/sudo pkill -F "$RUN_DIR/offpid.pid" 2>/dev/null || true
/usr/bin/sudo pkill -F "$RUN_DIR/metarpid.pid" 2>/dev/null || true
/usr/bin/sudo /usr/bin/python3 "$APP_DIR/metar.py" & echo $! | /usr/bin/sudo /usr/bin/tee "$RUN_DIR/metarpid.pid" >/dev/null
