# SD Card Flashing Runbook

This is the recommended path for building the gift Pi from a blank SD card.

## Recommended Flow

1. Finalize the board configuration in this repo.
2. Flash Raspberry Pi OS Lite to the SD card.
3. Boot the Pi on your own network for staging.
4. SSH in once.
5. Clone or copy this finalized repo to the Pi.
6. Run `sudo ./install.sh`.
7. Test the LEDs, mini display, reboot behavior, and BerryLan Wi-Fi setup.
8. Give Dad the finished map. He uses BerryLan if his home network is not already configured.

Do not manually install NeoPixel packages, cron jobs, or display libraries first. The installer does that so the build stays repeatable.

## Flash The SD Card

Use Raspberry Pi Imager.

Choose:

- Device: your Raspberry Pi model.
- OS: Raspberry Pi OS Lite, 64-bit if supported by your Pi.
- Storage: the SD card.

Open the Imager customization settings before writing.

Set:

- Hostname: `metarmap`
- Username: `pi`
- Password: choose a password you will know
- SSH: enabled
- Locale/time zone: your local time zone
- Wi-Fi: your home/staging Wi-Fi, optional but recommended for first setup

Using the `pi` username keeps the install path simple: `/home/pi/NYC_METARMap`.

Write the card, eject it, put it in the Pi, and boot it.

## First SSH Login

Wait a couple of minutes, then try:

```bash
ssh pi@metarmap.local
```

If that does not resolve, look up the Pi's IP address in your router and use:

```bash
ssh pi@PI_IP_ADDRESS
```

If the Pi is powered on but unreachable, use [Lost Pi Recovery](PI_RECOVERY.md). In many cases, reflashing is the fastest fix for a half-configured card.

## Install The Map Software

On the Pi:

```bash
cd /home/pi
git clone https://github.com/amigl001/NYC_METARMap.git
cd /home/pi/NYC_METARMap
python3 tools/validate_board_config.py
sudo ./install.sh
```

If you are testing local changes that are not pushed to GitHub yet, copy the repo from your Mac instead:

```bash
scp -r /Users/anthonymigliore/Desktop/dads_airport_gift/NYC_METARMap pi@metarmap.local:/home/pi/NYC_METARMap
```

Then SSH in and run:

```bash
cd /home/pi/NYC_METARMap
python3 tools/validate_board_config.py
sudo ./install.sh
```

## Verify Before Gifting

Run:

```bash
systemctl status metarmap-wifi-setup.service
systemctl status metarmap.timer
systemctl status metarmap-lights-off.timer
sudo systemctl start metarmap.service
journalctl -u metarmap.service -n 80 --no-pager
```

Then reboot:

```bash
sudo reboot
```

After reboot, confirm the map updates on its own.

## Test Dad's Wi-Fi Setup Flow

To test the recovery path, remove or disconnect the staging Wi-Fi from the Pi and reboot. Use the BerryLan app to connect the Pi back to Wi-Fi over Bluetooth.

After BerryLan reconnects Wi-Fi, SSH back in and confirm the map refresh service runs.

## Final Handoff

Before giving it to Dad:

- Confirm `airports` matches the physical board.
- Confirm `python3 tools/validate_board_config.py` passes.
- Confirm the LEDs match real airport positions.
- Confirm the mini display works.
- Confirm BerryLan can reconnect the Pi when Wi-Fi is unavailable.
- Give Dad only the short instructions in `DAD_SETUP.md`.
