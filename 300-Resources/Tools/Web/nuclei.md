---
tags: [tool, web, scanner, vulnerability]
tool: "nuclei"
category: "Web"
installed: true
phase: [scan, exploitation]
---

# nuclei - Template-Based Vulnerability Scanner

## Tool Overview
**Purpose:** Vulnerability scanning using YAML templates
**Location:** `which nuclei`
**Version:** `nuclei -version`
**Templates:** ~/nuclei-templates/

## When to Use
- Scanning for known CVEs
- Checking for misconfigurations
- Automated vulnerability detection
- After initial recon to find low-hanging fruit

## Why This Tool
**Strengths:**
- 5000+ community templates constantly updated
- Extremely fast (multi-threaded Go)
- Templates for everything (CVE, misconfigs, exposed panels)
- Workflow support for complex scans

## How to Use It

### Basic Scan
nuclei -u https://target.com

### Scan with Specific Templates
nuclei -u https://target.com -t cves/ -t misconfiguration/

### Update Templates
nuclei -update-templates

## Related Tools
- httpx
- katana
- subfinder

## Resources
- [nuclei Documentation](https://nuclei.projectdiscovery.io/)
