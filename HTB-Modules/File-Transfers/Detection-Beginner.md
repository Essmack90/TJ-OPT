---
tags: [module/file-transfers, detection, user-agent, blue-team, monitoring, level/beginner]
---

# Detection - Beginner's Guide

## Why Detection Matters

As a defender, you need to know what malicious file transfers look like. Attackers use the same tools we've been learning, and they leave traces.

**The Rule:** If you know what to look for, you can catch them in the act.

---

## Blacklisting vs Whitelisting

| Approach | Description | Effectiveness |
|----------|-------------|---------------|
| Blacklisting | Block known bad things | Easy to bypass |
| Whitelisting | Allow only known good things | Very effective, harder to setup |

**The Problem:** Blacklisting is easy to bypass with simple obfuscation. Whitelisting is time-consuming to set up but much more robust.

---

## What is a User Agent?

When an HTTP client connects to a web server, it sends a User-Agent string to identify itself.

Examples:
- Firefox: "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
- Chrome: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
- cURL: "curl/7.68.0"
- Python: "Python-urllib/3.8"

---

## Why User Agents Matter for Detection

Every tool has a default User-Agent. Attackers often forget to change them.

If you see:
- "Microsoft BITS/7.8" downloading an EXE
- "Microsoft-CryptoAPI/10.0" downloading from a strange IP
- PowerShell User-Agents from non-admin workstations

**That's suspicious.**

---

## Common Malicious User Agents

### PowerShell Invoke-WebRequest

User-Agent: Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.14393.0

### PowerShell WinHttpRequest

User-Agent: Mozilla/4.0 (compatible; Win32; WinHttp.WinHttpRequest.5)

### PowerShell Msxml2

User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; Win64; x64; Trident/7.0; .NET4.0C; .NET4.0E)

### Certutil

User-Agent: Microsoft-CryptoAPI/10.0

### BITS

User-Agent: Microsoft BITS/7.8

---

## Building a Detection Strategy

### Step 1: Know Your Baseline

What's normal in your environment?
- What user agents do your updates use?
- What do legitimate PowerShell scripts look like?
- What tools do your admins use?

### Step 2: Collect Logs

- Web server logs
- Proxy logs
- Firewall logs
- Endpoint logs (Sysmon, EDR)

### Step 3: Look for Anomalies

- PowerShell user agents from non-admin workstations
- Certutil downloading from internet
- BITS transfers to unusual destinations
- User agents that don't match your baseline

### Step 4: Investigate

When you see something suspicious:
- What was downloaded?
- Who ran it?
- When did it happen?
- What else happened around that time?

---

## User Agent Resources

| Resource | Purpose |
|----------|---------|
| https://useragentstring.com | Look up user agent strings |
| https://developers.whatismybrowser.com/useragents/explore/ | Browse common user agents |

---

## Key Takeaways

- Blacklisting is easy to bypass
- Whitelisting is more effective but harder to set up
- User agents identify HTTP clients
- Every tool has a default user agent
- Attackers often forget to change them
- PowerShell, BITS, and Certutil have distinct user agents
- Build a baseline of normal in your environment
- Collect logs from web servers, proxies, and endpoints
- Investigate anomalies
- This is just the beginning of detection
- Later modules will cover threat hunting in depth
