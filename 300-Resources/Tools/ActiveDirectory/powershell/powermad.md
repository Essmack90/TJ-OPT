---
tags: [tool, activedirectory, powershell]
tool: "powermad"
category: "Active Directory"
installed: true
phase: [exploitation]
---

# Powermad - Machine Account Manipulation

## Tool Overview
Purpose: PowerShell module for machine account attacks
Location: ~/tools/activedirectory/windows/Powermad.ps1

## How to Use It
powershell -ep bypass
Import-Module .\Powermad.ps1
New-MachineAccount -MachineAccount attacker -Password $(ConvertTo-SecureString 'Password123!' -AsPlainText -Force)

## Related Tools
powerview, rubeus
