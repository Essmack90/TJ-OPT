---
tags: [module/footprinting, windows, rdp, winrm, wmi, remote-access, level/beginner]
---

# Windows Remote Management - Beginner's Guide

## Why Remote Management Matters on Windows

Windows servers are often managed remotely. Instead of sitting at the console, administrators connect from their workstations to manage servers across the building or across the world.

Three main protocols handle this:

| Protocol | Ports | Purpose |
|----------|-------|---------|
| RDP | 3389 (TCP/UDP) | Full GUI desktop access |
| WinRM | 5985 (HTTP), 5986 (HTTPS) | Command-line remote management |
| WMI | 135 + dynamic | Deep system management and queries |

---

## RDP - Remote Desktop Protocol

RDP gives you a full GUI desktop on a remote Windows machine. It's like sitting at the computer.

### Key Features

- Full graphical interface
- Clipboard sharing
- Drive mapping
- Printer redirection
- Audio support
- Multiple monitor support

### Default Port

TCP 3389 (UDP 3389 also used)

### Security

Since Windows Vista, RDP supports TLS/SSL encryption. However, by default, certificates are self-signed, so you'll see a warning.

### Network Level Authentication (NLA)

NLA requires the client to authenticate BEFORE creating a full RDP session. This is more secure and the default on modern Windows.

---

## RDP Footprinting

### Nmap Scan

nmap -sV -sC 10.129.201.248 -p3389 --script rdp*

Output:
PORT     STATE SERVICE       VERSION
3389/tcp open  ms-wbt-server Microsoft Terminal Services
| rdp-enum-encryption: 
|   CredSSP (NLA): SUCCESS
|   CredSSP with Early User Auth: SUCCESS
|_  RDSTLS: SUCCESS
| rdp-ntlm-info: 
|   Target_Name: ILF-SQL-01
|   NetBIOS_Domain_Name: ILF-SQL-01
|   DNS_Computer_Name: ILF-SQL-01
|   Product_Version: 10.0.17763
|_  System_Time: 2021-11-06T13:46:00+00:00

### What This Reveals

- Hostname: ILF-SQL-01
- Windows version/build
- NLA is enabled
- System time

---

## Connecting to RDP from Linux

### xfreerdp

xfreerdp /u:cry0l1t3 /p:"P455w0rd!" /v:10.129.201.248

### rdesktop (older)

rdesktop -u cry0l1t3 -p P455w0rd! 10.129.201.248:3389

### Remmina (GUI)

Use the Remmina GUI client for easy connection management.

---

## RDP Security Check Tool

rdp-sec-check.pl analyzes RDP security settings.

### Installation

git clone https://github.com/CiscoCXSecurity/rdp-sec-check.git
cd rdp-sec-check
perl rdp-sec-check.pl 10.129.201.248

### What It Checks

- Supported protocols (RDP, TLS, CredSSP)
- Encryption methods
- NLA requirements
- Security weaknesses

---

## WinRM - Windows Remote Management

WinRM is a command-line remote management protocol. Think of it as "SSH for Windows" (but not exactly).

### Default Ports

| Port | Protocol | Encryption |
|------|----------|------------|
| 5985 | HTTP | None (but traffic can be encrypted) |
| 5986 | HTTPS | SSL/TLS |

### Why WinRM Matters

- Used by PowerShell remoting
- Allows remote command execution
- Can manage multiple servers centrally
- Enabled by default on Windows Server 2012+

---

## WinRM Footprinting

### Nmap Scan

nmap -sV -sC 10.129.201.248 -p5985,5986

Output:
5985/tcp open  http    Microsoft HTTPAPI httpd 2.0
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0

### Test WinRM Connection with PowerShell (Windows)

Test-WsMan -ComputerName 10.129.201.248

### Connect with Evil-WinRM (Linux)

evil-winrm -i 10.129.201.248 -u Cry0l1t3 -p P455w0rD!

Once connected:
*Evil-WinRM* PS C:\Users\Cry0l1t3\Documents>

---

## WMI - Windows Management Instrumentation

WMI is Windows's powerful management interface. It can read and modify almost any system setting.

### How WMI Works

1. Initial connection on TCP port 135
2. Connection moves to a random high port
3. Authenticated session established
4. Queries and commands can be executed

### What WMI Can Do

- Query system information
- Start/stop services
- Create processes
- Modify registry
- Enumerate users/groups
- Install software
- Reboot systems

---

## WMI Footprinting

### Using wmiexec.py (Impacket)

/usr/share/doc/python3-impacket/examples/wmiexec.py Cry0l1t3:"P455w0rD!"@10.129.201.248 "hostname"

Output:
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation
[*] SMBv3.0 dialect used
ILF-SQL-01

### Other WMI Tools

| Tool | Purpose |
|------|---------|
| wmic | Windows command-line WMI client |
| wmiclient.py | Impacket's WMI client |
| wmiexec.py | Execute commands via WMI |
| wmiquery.py | Run WQL queries |

---

## Key Takeaways

- RDP gives GUI access (port 3389)
- WinRM gives command-line access (ports 5985/5986)
- WMI is the deep management interface (port 135 + dynamic)
- NLA requires authentication before RDP session starts
- Self-signed certificates are normal but produce warnings
- WinRM is essential for PowerShell remoting
- Evil-WinRM is the best Linux tool for WinRM
- Impacket's wmiexec.py is great for WMI access
- Always check for default credentials
- These services are high-value targets in Windows environments
