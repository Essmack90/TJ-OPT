---
tags: [tool, wireless, wifi, phishing]
tool: wifiphisher
category: Wireless
installed: true
---

# Wifiphisher - Evil Twin Attack Framework

## Overview
Creates rogue access points to perform Evil Twin and KARMA attacks for credential harvesting

## Location
/usr/bin/wifiphisher

## Usage

### Basic Attack
sudo wifiphisher

### Choose Specific AP
sudo wifiphisher -aI wlan0 -jI wlan0 --essid "Target WiFi"

### Firmware Upgrade Page Attack
sudo wifiphisher --essid "Target WiFi" --phish-phrases "firmware,update"

### KARMA Attack
sudo wifiphisher --karma

### Phishing Scenarios
1. Firmware Upgrade Page (captures WPA passwords)
2. Browser Plugin Update (injects JavaScript)
3. OAuth Login Page (captures credentials)
4. Generic Login Page

## Commands in Client
Ctrl+C : Stop attack
Tab : Switch between screens
