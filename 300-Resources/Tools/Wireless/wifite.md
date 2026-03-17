---
tags: [tool, wireless, wifi]
tool: wifite
category: Wireless
installed: true
---

# Wifite - Automated Wireless Attack Tool

## Overview
Automated wireless attack tool that handles the entire process from target selection to cracking

## Location
/usr/bin/wifite

## Usage

### Basic Attack
sudo wifite

### Target Specific Network
sudo wifite --bssid AA:BB:CC:DD:EE:FF

### WPS-Only Attack
sudo wifite --wps

### PMKID-Only Attack
sudo wifite --pmkid

### Use Custom Wordlist
sudo wifite --dict /path/to/wordlist.txt

### Options
--wep : WEP attacks only
--wpa : WPA attacks only
--wps : WPS attacks only
--pmkid : PMKID attacks only
--dict : Custom wordlist
