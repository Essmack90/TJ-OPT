---
tags: [tool, wireless, wifi, pmkid]
tool: hcxtools
category: Wireless
installed: true
---

# hcxtools - PMKID Capture Tools

## Overview
Capture and convert PMKID hashes for WPA3/WPA2 attacks (no clients needed)

## Location
/usr/bin/hcxdumptool
/usr/bin/hcxpcaptool
/usr/bin/hcxpcapngtool

## Usage

### Capture PMKID
sudo hcxdumptool -i wlan0 -o capture.pcapng --enable_status=1

### Filter to Hashcat Format
hcxpcaptool -z pmkid.hashes capture.pcapng

### Crack with Hashcat
hashcat -m 16800 pmkid.hashes wordlist.txt

### Convert PCAP to Hashcat
hcxpcapngtool -o hash.hc22000 capture.pcapng

### Workflow
1. sudo hcxdumptool -i wlan0 -o capture.pcapng
2. hcxpcaptool -z hashes.txt capture.pcapng
3. hashcat -m 16800 hashes.txt wordlist.txt
