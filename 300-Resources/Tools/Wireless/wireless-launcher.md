---
tags: [tool, wireless, helper]
tool: wireless-launcher
category: Wireless
installed: true
---

# Wireless Launcher - Monitor Mode Helper

## Overview
Quick wireless interface setup script for enabling monitor mode

## Location
~/tools/wireless/launcher.sh

## Usage

### Run Launcher
sudo ~/tools/wireless/launcher.sh

### What It Does
1. Lists available wireless interfaces
2. Kills interfering processes
3. Brings interface down
4. Enables monitor mode
5. Brings interface up
6. Shows interface status

### After Launcher
airodump-ng wlan0
wifite
aireplay-ng -0 5 -a BSSID wlan0

### Manual Alternative
sudo airmon-ng check kill
sudo ip link set wlan0 down
sudo iw dev wlan0 set type monitor
sudo ip link set wlan0 up
iwconfig
