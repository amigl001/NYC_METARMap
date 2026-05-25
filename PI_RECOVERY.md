# Lost Pi Recovery

Use this when the Raspberry Pi is powered on but you cannot SSH into it because it is not connected to Wi-Fi.

## Fastest Recommendation

If there is nothing important on the SD card, reflash it using [SD_CARD_FLASHING.md](SD_CARD_FLASHING.md). For this project, a clean rebuild is usually faster and safer than guessing what network state is on the card.

## Option 1: Plug In Ethernet

If the Pi has Ethernet, this is the easiest rescue.

1. Plug the Pi into the router with Ethernet.
2. Wait one or two minutes.
3. Try:

```bash
ssh pi@metarmap.local
```

If that does not work, look in the router's connected devices list and SSH to the Pi's IP address:

```bash
ssh pi@PI_IP_ADDRESS
```

Once connected, fix Wi-Fi:

```bash
nmcli device wifi list
sudo nmcli device wifi connect "YOUR_WIFI_NAME" password "YOUR_WIFI_PASSWORD"
nmcli connection show --active
```

## Option 2: HDMI And Keyboard

If Ethernet is not available, connect the Pi to a monitor and keyboard.

Log in with the user configured in Raspberry Pi Imager, then run:

```bash
nmcli device wifi list
sudo nmcli device wifi connect "YOUR_WIFI_NAME" password "YOUR_WIFI_PASSWORD"
ip addr show wlan0
```

After that, SSH should work again from your computer.

## Option 3: Reflash

This is the cleanest option if the current SD card is only a half-working setup.

1. Flash Raspberry Pi OS Lite again.
2. In Raspberry Pi Imager, set:
   - Hostname: `metarmap`
   - Username: `pi`
   - SSH: enabled
   - Wi-Fi: your current setup Wi-Fi
3. Boot the Pi.
4. SSH in and run the installer from [SD_CARD_FLASHING.md](SD_CARD_FLASHING.md).

## After Recovery

Once you are back in, install this project's appliance setup:

```bash
cd /home/pi/NYC_METARMap
python3 tools/validate_board_config.py
sudo ./install.sh
```

After that, if the Pi loses Wi-Fi in the future, it should create the `METARMap Setup` hotspot instead of disappearing.
