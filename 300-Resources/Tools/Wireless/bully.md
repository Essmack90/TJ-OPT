---
tags: [tool, wireless, wifi, wps]
tool: bully
category: Wireless
installed: true
---

# Bully - WPS PIN Brute Force (Alternative)

## Overview
Alternative WPS brute force tool with better lockout handling

## Location
/usr/bin/bully

## Usage

### Basic Attack
sudo bully wlan0mon -b AA:BB:CC:DD:EE:FF

### With Delay
sudo bully wlan0mon -b AA:BB:CC:DD:EE:FF -d 5

### WPS Pixie-Dust Attack
sudo bully wlan0mon -b AA:BB:CC:DD:EE:FF --pixiewps

### Options
-d : Delay between attempts
-p : PIN index to start from
-e : Target SSID
-F : Force bruteforce (ignore detection)
--pixiewps : Use Pixie-Dust attack

## Reaver vs Bully
Reaver: More common, but slower with lockouts
Bully: Better lockout handling, Pixie-Dust support
