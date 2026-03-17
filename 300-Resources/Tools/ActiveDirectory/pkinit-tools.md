---
tags: [tool, activedirectory, kerberos]
tool: "pkinit-tools"
category: "Active Directory"
installed: true
phase: [exploitation]
---

# PKINITtools - Kerberos PKINIT Abuse

## Tool Overview
Purpose: Tools for PKINIT abuse and certificate attacks
Location: ~/tools/activedirectory/PKINITtools/

## Key Scripts
- gets4uticket.py - Get S4U ticket
- getnthash.py - Get NT hash from PKINIT

## How to Use It
python3 gets4uticket.py kerberos+pkinit://domain.local/user@dc.domain.local:88/DC$@domain.local -key pfx-key -pfx-base64 $(base64 -w0 cert.pfx)

## Related Tools
certipy, pywhisker
