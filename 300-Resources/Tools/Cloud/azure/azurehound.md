---
tags: [tool, cloud, azure, bloodhound]
tool: "azurehound"
category: "Cloud"
installed: true
phase: [recon, analysis]
---

# AzureHound - BloodHound for Azure

## Tool Overview
Purpose: Azure AD enumeration for BloodHound
Location: /usr/bin/azurehound

## When to Use
- Azure AD reconnaissance
- Attack path discovery
- Relationship mapping

## How to Use It

Collect Azure AD data:
azurehound -u user@domain.com -p pass list

Collect with tokens:
azurehound -t ACCESS_TOKEN list

Output to BloodHound:
azurehound -u user@domain.com -p pass -o azurehound.json

## Related Tools
bloodhound, microburst
