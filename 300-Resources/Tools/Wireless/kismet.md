---
tags: [tool, wireless, wifi, bluetooth, sdr]
tool: kismet
category: Wireless
installed: true
---

# Kismet - Wireless Monitor/IDS

## Overview
Wireless network detector, sniffer, and intrusion detection system

## Location
/usr/bin/kismet

## Usage

### Start Kismet
sudo kismet

### Web UI
http://localhost:2501

### Command Line Mode
sudo kismet -c wlan0,wlan1

### Log to File
sudo kismet --daemonize --log-type pcap --log-name kismet-log

### Sources
wlan0 : WiFi monitoring
hci0 : Bluetooth monitoring
rtl433 : SDR weather sensors

### Features
- Detects WiFi, Bluetooth, SDR devices
- Real-time graphing
- Geolocation mapping
- PCAP logging
- Plugin support
- Network fingerprinting
