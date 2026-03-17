---
tags: [tool, activedirectory, dcom]
tool: "dcomrade"
category: "Active Directory"
installed: true
phase: [enumeration]
---

# DCOMrade - DCOM Enumeration

## Tool Overview
Purpose: Enumerate DCOM applications for lateral movement
Location: ~/tools/activedirectory/DCOMrade/dcomrade.py

## How to Use It
python3 dcomrade.py -d domain.local -u user -p pass -t target-ip

## Related Tools
dcomexec.py, impacket
