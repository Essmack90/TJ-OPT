---
tags: [tool, cloud, azure, enumeration]
tool: "microburst"
category: "Cloud"
installed: true
phase: [recon, enumeration]
---

# MicroBurst - Azure Enumeration Framework

## Tool Overview
Purpose: PowerShell toolkit for Azure enumeration
Location: ~/tools/cloud/MicroBurst

## When to Use
- Azure environment enumeration
- Storage account discovery
- Role assignment checking

## How to Use It

Start PowerShell:
pwsh

Import module:
Import-Module ./MicroBurst/MicroBurst.psm1

Enumerate storage:
Get-AzureDomainInfo

## Key Functions
- Get-AzureDomainInfo - Enumerate Azure resources
- Invoke-EnumerateAzureBlobs - Find storage accounts
- Get-AzurePasswords - Extract credentials

## Related Tools
azure-cli, stormspotter
