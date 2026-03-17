---
tags: [tool, wireless, wifi, cracking]
tool: cowpatty
category: Wireless
installed: true
---

# cowpatty - WPA Handshake Cracker

## Overview
Offline dictionary attack tool for WPA/WPA2-PSK using captured 4-way handshakes

## Location
/usr/bin/cowpatty

## Usage

### Basic Crack
cowpatty -r capture.cap -f wordlist.txt -s MyWiFi

### With Precomputed Hash (genpmk)
genpmk -f wordlist.txt -d precomputed.hash -s MyWiFi
cowpatty -r capture.cap -d precomputed.hash -s MyWiFi

### Options
-r : Capture file
-f : Wordlist
-d : Precomputed hash file
-s : Target SSID

### Precompute Hashes
genpmk -f rockyou.txt -d wpa2.hash -s TargetWiFi
