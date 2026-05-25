# Dad Setup Guide

This version is meant to behave like an appliance: plug it in, give it Wi-Fi from a phone if needed, and let it run.

## What Dad Does

1. Plug in the METARMap.
2. Wait about two minutes.
3. If the lights start updating, it is already connected.
4. If the lights do not update, open Wi-Fi settings on a phone.
5. Join `METARMap Setup`.
6. Use password `metarmap1`.
7. Open `http://10.42.0.1:8080`.
8. Pick the home Wi-Fi network and enter the Wi-Fi password.
9. Wait about two minutes. The setup network should disappear and the map should begin updating.

If the password was typed wrong, the `METARMap Setup` network comes back after a short delay. Join it again and retry.

## What You Do Before Gifting It

Update `airports` so it matches the exact LEDs on the finished board. Use airport codes for real airport LEDs and `NULL` for physical spacer LEDs that should stay dark. Then run:

```bash
python3 tools/validate_board_config.py
```

Once the board configuration passes, follow the full [SD card flashing runbook](SD_CARD_FLASHING.md). The short version is: flash Raspberry Pi OS Lite, enable SSH, use the `pi` username, boot the Pi, SSH in, and run:

```bash
cd /home/pi
git clone https://github.com/amigl001/NYC_METARMap.git
cd /home/pi/NYC_METARMap
sudo ./install.sh
```

Then confirm:

```bash
systemctl status metarmap-wifi-setup.service
systemctl status metarmap.timer
systemctl status metarmap-lights-off.timer
```

The installer enables:

- A Wi-Fi setup portal at `http://10.42.0.1:8080` whenever the map is not connected to home Wi-Fi.
- A METAR refresh every five minutes after boot.
- A lights-off schedule at 10:05 PM.
- I2C support for the mini display.

## Wi-Fi Recovery

If Dad changes router names or passwords later:

1. Unplug the map.
2. Plug it back in.
3. Wait about two minutes.
4. Join `METARMap Setup` from a phone.
5. Open `http://10.42.0.1:8080`.
6. Enter the new Wi-Fi info.

## Useful Service Commands

```bash
sudo systemctl restart metarmap-wifi-setup.service
sudo systemctl restart metarmap.service
sudo systemctl status metarmap.service
journalctl -u metarmap.service -n 80 --no-pager
journalctl -u metarmap-wifi-setup.service -n 80 --no-pager
```

## Notes

- The Pi must use NetworkManager. Raspberry Pi OS Bookworm does this by default.
- The setup hotspot uses `METARMap Setup` / `metarmap1`.
- The app expects the project at `/home/pi/NYC_METARMap`.
- The airport list is controlled by `airports`, but that should be treated as factory configuration before gifting.
