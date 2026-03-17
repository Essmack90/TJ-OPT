---
tags: [tool, wireless, wifi]
tool: aircrack-ng
category: Wireless
installed: true
---

# aircrack-ng - WiFi Security Assessment Suite

## Overview
Complete suite for monitoring, attacking, and cracking WiFi networks

## Location
/usr/bin/aircrack-ng

## Key Commands

### airmon-ng - Monitor mode management
airmon-ng check kill
airmon-ng start wlan0
airmon-ng stop wlan0mon

### airodump-ng - Packet capture
airodump-ng wlan0mon
airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

### aireplay-ng - Packet injection
aireplay-ng -0 5 -a AA:BB:CC:DD:EE:FF wlan0mon

### aircrack-ng - WEP/WPA cracking
aircrack-ng -w wordlist.txt capture-01.cap
aircrack-ng -w wordlist.txt -b AA:BB:CC:DD:EE:FF capture-01.cap

## Basic Workflow
1. airmon-ng start wlan0
2. airodump-ng wlan0mon
3. airodump-ng -c CH -b BSSID -w capture wlan0mon
4. aireplay-ng -0 5 -a BSSID wlan0mon
5. aircrack-ng -w wordlist.txt capture-01.cap
