---
tags: [tool, activedirectory, bloodhound, powershell]
tool: "sharphound-ps1"
category: "Active Directory"
installed: true
phase: [enumeration]
---

# SharpHound.ps1 - PowerShell BloodHound Collector

## Tool Overview
Purpose: PowerShell version of SharpHound for BloodHound data collection
Location: ~/tools/activedirectory/windows/SharpHound.ps1

## How to Use It
powershell -ep bypass
. .\SharpHound.ps1
Invoke-BloodHound -CollectionMethod All

## Related Tools
bloodhound, sharphound.exe
