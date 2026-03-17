---
tags: [tool, activedirectory, automation]
tool: "linwinpwn"
category: "Active Directory"
installed: true
phase: [enumeration, exploitation]
---

# linWinPwn - Automated AD Enum Framework

## Tool Overview
Purpose: Automated AD enumeration and exploitation
Location: ~/tools/activedirectory/linWinPwn/linWinPwn.sh

## How to Use It

Basic Scan:
./linWinPwn.sh -d domain.local -u user -p pass -t dc-ip

Interactive Mode:
./linWinPwn.sh -d domain.local -u user -p pass -t dc-ip -i

## Related Tools
bloodhound-python, crackmapexec
