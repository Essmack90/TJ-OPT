---
tags: [tool, activedirectory, powershell]
tool: "powerview"
category: "Active Directory"
installed: true
phase: [enumeration]
---

# PowerView - AD PowerShell Enumeration

## Tool Overview
Purpose: PowerShell module for AD reconnaissance
Location: ~/tools/activedirectory/windows/PowerView.ps1

## When to Use
- When you have PowerShell access
- AD enumeration from Windows
- Finding attack paths

## How to Use It

Load PowerView:
powershell -ep bypass
Import-Module .\PowerView.ps1

Find Domain Admins:
Get-NetGroupMember -GroupName "Domain Admins"

Find Domain Computers:
Get-NetComputer

Find Domain Users:
Get-NetUser | select samaccountname

Find Domain Shares:
Invoke-ShareFinder

Find Local Admin Access:
Find-LocalAdminAccess

## Related Tools
ADModule, BloodHound
