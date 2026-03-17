---
tags: [tool, activedirectory, ldap]
tool: "windapsearch"
category: "Active Directory"
installed: true
phase: [enumeration]
---

# windapsearch - LDAP Search Tool

## Tool Overview
Purpose: Enumerate AD users, groups, computers via LDAP
Location: ~/tools/activedirectory/windapsearch/windapsearch.py

## How to Use It
python3 windapsearch.py -d domain.local -u user@domain.local -p pass --dc dc.domain.local -U
python3 windapsearch.py -d domain.local -u user@domain.local -p pass --dc dc.domain.local -G
python3 windapsearch.py -d domain.local -u user@domain.local -p pass --dc dc.domain.local -C

## Related Tools
ldapsearch, ldapdomaindump
