---
tags: [tool, wireless, wifi, wps]
tool: reaver
category: Wireless
installed: true
---

# Reaver - WPS PIN Brute Force

## Overview
Brute-force WPS PINs to recover WPA/WPA2 passphrases

## Location
/usr/bin/reaver

## Usage

### Basic Attack
sudo reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -vv

### With Delay (avoid lockout)
sudo reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -d 5 -vv

### Ignore Lockouts
sudo reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -L -vv

### 5GHz Band
sudo reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -5 --channel 149 -vv

### Options
-i : Interface in monitor mode
-b : Target BSSID
-vv : Verbose output
-d : Delay between attempts (seconds)
-L : Ignore lockouts
-5 : Use 5GHz band
-E : Terminate early
