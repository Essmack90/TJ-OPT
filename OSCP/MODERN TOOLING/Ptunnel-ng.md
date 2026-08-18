# Ptunnel-ng

ICMP tunneling tool. Wraps TCP connections inside ICMP echo request/reply packets, allowing TCP traffic (including SSH) to pass through environments where only ICMP (ping) traffic is permitted outbound. A modern rewrite of the original ptunnel project.

Cross-links: [[Pivoting, Tunneling, and Port Forwarding (HTB Supplementary)#PT.6 ICMP Tunneling with ptunnel-ng|PT.6]], [[Port Redirection and SSH Tunneling (Command Appendix)#ptunnel-ng (ICMP Tunneling)|Command Appendix]], [[Pivoting & Tunneling (Breakdowns)#ptunnel-ng static build: the autogen.sh sed patch and why static linking|Command Breakdowns]]

---

## What problem it solves

When a firewall drops all TCP/UDP but passes ICMP (ping), ptunnel-ng wraps TCP data inside ICMP echo packets. The pivot host runs ptunnel-ng in server mode; Kali runs it in client mode and connects to a local TCP port that maps through the ICMP channel to an SSH port (or any TCP service) on the pivot.

## Install and build (static binary required)

ptunnel-ng must be built as a **static binary** on Kali so it runs on the pivot host without library dependency issues. The build process modifies `autogen.sh` to inject the static-link flags:

```bash
git clone https://github.com/utoni/ptunnel-ng.git
cd ptunnel-ng

# Patch autogen.sh to add static-link flags before running it
sed -i '$s/.*/LDFLAGS=-static "${NEW_WD}\/configure" --enable-static $@ \&\& make clean \&\& make -j${BUILDJOBS:-4} all/' autogen.sh
./autogen.sh

# Verify it's actually static:
file ptunnel-ng/src/ptunnel-ng   # should include "statically linked"
ldd ptunnel-ng/src/ptunnel-ng    # should say "not a dynamic executable"
```

Transfer the binary to the pivot:
```bash
scp ptunnel-ng/src/ptunnel-ng user@<PIVOT_IP>:~/ptunnel-ng
```

## Usage

```bash
# On the pivot host (server mode):
# -r <pivot_ip>: the IP ptunnel-ng server binds to (pivot's own IP)
# -R 22: the internal TCP port to forward (SSH in this case)
sudo ./ptunnel-ng -r <PIVOT_IP> -R 22

# On Kali (client mode):
# -p <pivot_ip>: connect to the ptunnel-ng server at this IP
# -l 2222: local TCP port on Kali to open (your tunnel entry point)
# -r <pivot_ip>: destination IP on the pivot's network (pivot itself here)
# -R 22: destination port (SSH)
sudo ./ptunnel-ng -p <PIVOT_IP> -l 2222 -r <PIVOT_IP> -R 22
```

Once the client is running, SSH through the ICMP tunnel on Kali:
```bash
ssh -p 2222 -lubuntu 127.0.0.1
```

Add proxychains SOCKS proxy on top of the SSH session:
```bash
ssh -D 9050 -p 2222 -lubuntu 127.0.0.1
# /etc/proxychains4.conf: socks5 127.0.0.1 9050
proxychains nmap -sT -Pn -n <internal_target>
```

## Caveats

- Requires **root on both sides** (raw ICMP socket access).
- Static build is mandatory for pivot transfer. A dynamically-linked binary will fail with library-not-found errors on the pivot.
- All ICMP traffic in the tunnel is tagged as echo request/reply from the ptunnel-ng process, which is different from normal `ping` traffic. Some deep-packet-inspection firewalls can detect and block it.
- Performance is limited by ICMP rate-limiting and round-trip latency.

#### Tags: #ModernTooling #ptunnel-ng #Pivoting #ICMPTunnel #StaticBuild #HTBSupplementary
