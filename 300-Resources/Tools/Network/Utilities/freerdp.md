---
tags: [tool, rdp, windows]
tool: "freerdp"
category: "Network Utilities"
installed: true
phase: [lateral]
---

# FreeRDP - RDP Client

## Overview
Free implementation of Remote Desktop Protocol

## Location
/usr/bin/xfreerdp

## Basic Usage
xfreerdp /v:target.com /u:user /p:pass
xfreerdp /v:target.com /dynamic-resolution +clipboard

## Common Options
/v : Target server
/u : Username
/p : Password
/dynamic-resolution : Auto-resize
+clipboard : Share clipboard

## Related Tools
rdesktop
