# Rpivot

HTTP-tunneled SOCKS4 proxy written in Python. Designed specifically for pivoting through environments where only HTTP/HTTPS outbound is allowed. Two components: a server script that runs on Kali, and a client script that runs on the pivot host.

Cross-links: [[19. Port Redirection and SSH Tunneling|PT.3]], [[Port Redirection and SSH Tunneling#Rpivot (HTTP-Tunneled SOCKS Proxy)|Command Appendix]]

---

## What problem it solves

When SSH is blocked at the firewall but outbound HTTP (port 80 or 443) is allowed, Rpivot tunnels a SOCKS proxy session inside a normal-looking HTTP stream. The pivot host only needs to make outbound HTTP connections to Kali; no listening port required on the pivot side.

## Install

```bash
sudo git clone https://github.com/klsecservices/rpivot.git
cd rpivot
# No build step needed. Pure Python scripts. Python 2.7 required on the client (pivot) side.
```

## Usage

```bash
# On Kali: start the server
# Port 9999 = the HTTP tunnel control port (client connects here)
# Port 9050 = the local SOCKS4 proxy port (proxychains connects here)
python2.7 server.py --proxy-port 9050 --server-port 9999 --server-ip 0.0.0.0

# On the pivot host: connect the client back to Kali (Python 2.7 required)
python2.7 client.py --server-ip <KALI_IP> --server-port 9999
```

Once connected, on Kali:
```
/etc/proxychains4.conf:  socks4 127.0.0.1 9050
proxychains nmap -sT -Pn -n <internal_target>
```

## Caveats

- Client side requires Python 2.7 specifically (not Python 3). May need to install on a modern pivot host.
- SOCKS4 only, no SOCKS5 or UDP support.
- HTTP-tunneled traffic is slower than SSH forwarding; latency stacks badly on deep scans.
- If the pivot is behind an NTLM-authenticated web proxy: `client.py` supports `--ntlm-proxy-ip`, `--ntlm-proxy-port`, `--username`, `--password`, `--domain` flags to authenticate through the corporate proxy.

## vs Chisel

Both Rpivot and Chisel forward over HTTP. Chisel is generally preferred in modern engagements because it's Go-compiled (single static binary, no Python dependency on the pivot), supports SOCKS5, and is actively maintained. Rpivot is Python-native and useful when Go binaries are blocked or unavailable.

#### Tags: #ModernTooling #Rpivot #Pivoting #HTTPTunnel #SOCKS #HTBSupplementary
## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

Rpivot supports a repeatable task in an authorized assessment; knowing when to use it keeps the workflow deliberate rather than tool-led.

## Tool description

Rpivot is a focused utility for the technique named by this page. Read its output as evidence and confirm important findings manually.

## Basic usage

Run the help screen first, then use the smallest command that answers the current question:

~~~bash
rpivot --help
~~~

## Related RUNBOOK V2 stage

- [[RUNBOOK V2/Index]] -- route to the technique-specific stage after identifying the finding

## Related module

- [[MODULES/13. Locating Public Exploits]] -- understand the tool’s place in a controlled workflow
