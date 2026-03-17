---
tags: [tool, wireless, embedded, exploit]
tool: routersploit
category: Wireless
installed: true
---

# RouterSploit - Embedded Device Exploitation

## Overview
Exploitation framework for routers and embedded devices

## Location
/usr/local/bin/routersploit (launcher)

## Usage

### Start RouterSploit
routersploit

### Scan Target
rsf > use scanners/autopwn
rsf > set target 192.168.1.1
rsf > run

### Search Exploits
rsf > search dlink
rsf > search credentials

### Use Module
rsf > use exploits/routers/dlink/dir815_creds
rsf > set target 192.168.1.1
rsf > check
rsf > exploit

### Credential Stuffing
rsf > use creds/default_creds
rsf > set target 192.168.1.1
rsf > run

### Modules
scanners/ : Target enumeration
exploits/ : Device exploits
creds/ : Default credential testing
payloads/ : Payload generation
