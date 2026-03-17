---
tags: [tool, cloud, azure]
tool: "azure-cli"
category: "Cloud"
installed: true
phase: [recon, exploitation]
---

# Azure CLI - Microsoft Azure Command Line Interface

## Tool Overview
Purpose: Official CLI for managing Azure services
Location: /usr/bin/az

## When to Use
- Azure environment enumeration
- Resource management
- Cloud exploitation

## How to Use It

Login to Azure:
az login

List resource groups:
az group list

List VMs:
az vm list

List storage accounts:
az storage account list

## Related Tools
MicroBurst, Stormspotter, AzureHound
