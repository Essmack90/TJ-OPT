---
tags: [tool, activedirectory, kerberos, relay]
tool: "krbrelayx"
category: "Active Directory"
installed: true
phase: [exploitation]
---

# krbrelayx - Kerberos Relay Attacks

## Tool Overview
Purpose: Kerberos relay attack tool
Location: ~/tools/activedirectory/krbrelayx/krbrelayx.py

## How to Use It

Basic Relay:
krbrelayx.py -t ldap://dc.domain.local

With Authentication:
krbrelayx.py -t ldap://dc.domain.local -u domain\\user -d domain.local -hashes :hash

## Related Tools
ntlmrelayx, responder
