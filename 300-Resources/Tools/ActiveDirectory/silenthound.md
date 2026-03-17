---
tags: [tool, activedirectory, enumeration]
tool: "silenthound"
category: "Active Directory"
installed: true
phase: [enumeration]
---

# silenthound - Stealthy AD Enumeration

## Tool Overview
Purpose: Low-and-slow AD enumeration to avoid detection
Location: ~/tools/activedirectory/silenthound/silenthound.py

## How to Use It
python3 silenthound.py -d domain.local -u user -p pass -dc dc.domain.local

## Related Tools
windapsearch, ldapdomaindump
