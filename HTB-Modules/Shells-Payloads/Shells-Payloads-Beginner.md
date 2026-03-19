---
tags: [module/shells-payloads, shells, payloads, reverse-shell, bind-shell, web-shell, level/beginner]
---

# Shells and Payloads - Beginner's Guide

## What is a Shell?

A shell is a program that provides an interface to interact with an operating system. It accepts commands and displays output.

Examples:
- Linux: Bash, Zsh, Sh
- Windows: cmd, PowerShell

**The Rule:** If you can get a shell, you can control the system.

---

## Why Do We Want Shells?

| Reason | Why It Matters |
|--------|----------------|
| Command execution | Run system commands |
| File access | Read/write files |
| Privilege escalation | Get more access |
| Persistence | Stay on the system |
| Pivoting | Move to other hosts |

**The Goal:** "I caught a shell!" means you have remote control of the target.

---

## Common Shell Phrases

| Phrase | Meaning |
|--------|---------|
| "I caught a shell" | Successfully gained remote access |
| "I popped a shell" | Exploited a vulnerability to get access |
| "I dropped into a shell" | Got interactive access |
| "I'm in!" | You have access |

---

## Types of Shells

### 1. Reverse Shell

Target connects BACK to you.

Your Machine (listener) <--- Target (connects)

**Pros:** Bypasses inbound firewalls
**Cons:** You need a public IP or port forwarding

### 2. Bind Shell

Target opens a port for you to connect TO.

Your Machine (connects) ---> Target (listener)

**Pros:** Works if target can't make outbound connections
**Cons:** Firewall may block inbound port

### 3. Web Shell

A script (PHP, ASP, JSP) that executes commands via web requests.

Your Browser ---> Web Server ---> Command Execution

**Pros:** Works through firewalls, uses port 80/443
**Cons:** Limited interactivity, may be logged

---

## What is a Payload?

A payload is code crafted to exploit a vulnerability and give you access.

| Context | Definition |
|---------|------------|
| Networking | The data portion of a packet |
| Exploitation | Code that exploits a vulnerability |
| Malware | The malicious action (ransomware, backdoor) |

**The Rule:** The payload delivers the shell.

---

## Payload Delivery Methods

| Method | Description |
|--------|-------------|
| Exploit | Payload embedded in exploit code |
| File upload | Upload malicious script to web server |
| Phishing | User executes payload via email |
| USB drop | Physical access |
| Drive-by download | Compromised website |

---

## Shell Perspectives

| Perspective | Description |
|-------------|-------------|
| Computing | Bash, Zsh, cmd, PowerShell (text-based interface) |
| Exploitation | Result of exploiting a vulnerability (EternalBlue gives cmd) |
| Web | Script uploaded to web server, accessed via browser |

---

## Why CLI Shells Beat GUI

| Advantage | Why |
|-----------|-----|
| Harder to detect | No graphical session to notice |
| Faster | Command line is faster than clicking |
| Automatable | Scripts can automate actions |
| Lightweight | Works over slow connections |

---

## Key Takeaways

- A shell gives you command execution on a target
- Reverse shell = target connects to you
- Bind shell = you connect to target
- Web shell = command execution via web server
- Payload = code that delivers the shell
- Different delivery methods for different situations
- CLI shells are stealthier than GUI
- "Catching a shell" is a major milestone in exploitation
- Practice all shell types in the lab
- The more you know, the more options you have
