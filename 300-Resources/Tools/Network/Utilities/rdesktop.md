---
tags: [tool, rdp, windows]
tool: "rdesktop"
category: "Network Utilities"
installed: true
phase: [lateral]
---

# rdesktop - RDP Client

## Overview
Remote Desktop Protocol client

## Location
/usr/bin/rdesktop

## Basic Usage
rdesktop target.com
rdesktop -u user target.com
rdesktop -f target.com (fullscreen)

## Common Options
-u : Username
-p : Password
-f : Fullscreen
-g : Resolution

## Related Tools
freerdp, xfreerdp
