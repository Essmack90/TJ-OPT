---
tags: [tool, cloud, azure, powershell]
tool: "powerzure"
category: "Cloud"
installed: true
phase: [recon, exploitation]
---

# PowerZure - PowerShell Azure Toolkit

## Tool Overview
Purpose: PowerShell framework for Azure exploitation
Location: ~/tools/cloud/PowerZure

## When to Use
- Azure post-exploitation
- Azure AD attacks
- Resource enumeration

## How to Use It

Start PowerShell:
pwsh

Import module:
Import-Module ./PowerZure/PowerZure.psm1

Enumerate Azure:
Get-AzureTarget

## Related Tools
azure-cli, microburst
