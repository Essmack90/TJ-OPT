---
tags: [tool, activedirectory, powershell]
tool: "admodule"
category: "Active Directory"
installed: true
phase: [enumeration]
---

# ADModule - Microsoft AD PowerShell Module

## Tool Overview
Purpose: Native PowerShell module for AD management
Location: ~/tools/activedirectory/windows/ADModule-master/

## How to Use It
Import-Module .\Microsoft.ActiveDirectory.Management.dll
Get-ADUser -Filter *
Get-ADComputer -Filter *
Get-ADGroupMember "Domain Admins"

## Related Tools
powerview, adexplorer
