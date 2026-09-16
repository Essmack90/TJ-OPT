---
box_sources: [Escape]
---

# Start Here

**Step 1 of 50 · Universal**

*Initialise the box workspace, set the variables, and run the full TCP scan.*

Fast syntax reference: [[OSCP COMMAND MASTER CHEATSHEET|OSCP Command Master Cheatsheet]] · This page owns workspace setup and evidence capture; the cheatsheet is the compact command lookup.

> [!tip] 💡 Follow-along mode
> If this is a genuinely new box, start at [[00 - Follow-Along Controller]] Step 0. This page is the first scan stage inside that controller.

> [!warning] 💡 Do not skip the output decision
> After the scan, open [[Port Triage]] and choose the row that matches your actual ports. Do not assume the machine is Linux, Windows, or AD from the box description alone.

## Run this

> **Why:** A full TCP scan finds every open port, including non-standard ports, so a service that is easy to miss does not become a missed foothold.

Run this page once at the beginning of a box. `boxstart` creates the working folders and saves the target variables; the Nmap command then finds every TCP service so the next page can choose the right path. If you want the complete hand-holding flow, use [[00 - Follow-Along Controller]] instead.

```bash
boxstart "BOX_NAME_HERE" "TARGET_IP_HERE" htb
```

Replace the two uppercase values before pressing Enter. Use `offsec` or `thm` instead of `htb` when appropriate. If the box is already loaded in another terminal, use `boxload` instead:

```bash
boxload
```

Then run the scan using the variables created by the helper:

```bash
boxset LocalIP "$(ip addr show tun0 2>/dev/null | awk '/inet / {sub(/\/.*/,"",$2); print $2; exit}')"
sudo nmap -Pn -n -sS -p- --min-rate 5000 "$BoxIP" -oA "$BoxDir/nmap/allports"
```

## Example output

```

[+] Box workspace ready: $BoxName
[+] Target: 10.10.10.1
...
Nmap scan completed
22/tcp open ssh
80/tcp open http
```

Focus on the port number and state first. `open` means the host answered, while `filtered` means the result needs a routing or firewall check. The full scan is complete when the command returns to the prompt and the saved `.nmap` file contains the final host result. Copy every open TCP port into the next service scan, then open [[Port Triage]].

## What did you get?

- [ ] The scan is still running → **Wait for it to finish, then go to Step 2 · [[Port Triage]]**
- [ ] Ports are listed in the output → **Go to Step 2 · [[Port Triage]]**
- [ ] The target is unreachable → **Run `ip addr show tun0` and `ping -c 1 $BoxIP`; if tun0 is absent, reconnect the VPN, then rerun this page**

## Notes

Keep all scan output under `$BoxDir/nmap/` and keep credentials in `$BoxDir/loot/`.

## Gotcha

> [!warning] 💡
> If `boxstart` is not found, load the Kali helper functions with `source ~/.zshrc` and retry. Do not manually invent a second workspace layout: the helper commands and later pages expect the folders and variables created by `boxstart`.
## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/CronOS|CronOS]] -- full TCP scan found SSH, DNS, and HTTP for the next routing decision
- *(no write-up yet)*
- [[OSCP/BOXES/WRITE UPS/Linux/Blocky|Blocky]] -- full TCP scan and helper workspace initialization
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- full TCP scan and helper workspace initialization
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- full TCP scan and helper workspace initialization
- [[OSCP/BOXES/WRITE UPS/Linux/Dawn2|Dawn2]] -- full TCP scan and helper workspace initialization
- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]] -- full TCP scan and helper workspace initialization
- [[OSCP/BOXES/WRITE UPS/Linux/Jarvis|Jarvis]] -- full TCP scan and helper workspace initialization
- [[OSCP/BOXES/WRITE UPS/Linux/SwagShop|SwagShop]] -- full TCP scan and helper workspace initialization
- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]] -- full TCP scan and helper workspace initialization
- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- full TCP scan and manual FreeBSD workspace initialization
- [[OSCP/BOXES/WRITE UPS/Linux/Valentine|Valentine]] -- full TCP scan and helper workspace initialization
- [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]] -- full TCP scan and helper workspace initialization
- [[OSCP/BOXES/WRITE UPS/Linux/SolidState|SolidState]] -- full TCP scan, target-IP reset handling, and helper workspace initialization
- [[OSCP/BOXES/WRITE UPS/AD/Active|Active]] -- full TCP scan and AD workspace initialization
- [[OSCP/BOXES/WRITE UPS/Windows/Conceal|Conceal]] -- full TCP and UDP scans, then IKE/IPSec service-gate discovery
- [[OSCP/BOXES/WRITE UPS/Windows/Bastard|Bastard]] -- full TCP scan and helper workspace initialization
- [[OSCP/BOXES/WRITE UPS/Linux/Knife|Knife]] -- full TCP scan and helper workspace initialization
- [[OSCP/BOXES/WRITE UPS/Linux/DevOops|DevOops]] -- full TCP scan found SSH and non-standard Gunicorn HTTP
- [[OSCP/BOXES/WRITE UPS/Windows/Love|Love]] -- full TCP scan found Apache/PHP, SMB, MariaDB, WinRM, and dynamic Windows services
- [[OSCP/BOXES/WRITE UPS/AD/Vintage|Vintage]] -- full TCP scan found the domain-controller service set and routed into Kerberos-first AD enumeration
- [[OSCP/BOXES/WRITE UPS/Windows/Optimum|Optimum]] -- full TCP scan found a single exposed HTTP service and routed into standalone Windows HFS enumeration
- [[OSCP/BOXES/WRITE UPS/Windows/Legacy|Legacy]] -- full TCP discovery preserved the classic RPC/NetBIOS/SMB footprint before exploit selection
- [[OSCP/BOXES/WRITE UPS/Linux/Busqueda|Busqueda]] -- full TCP discovery identified SSH and Apache before the hostname-aware Searchor web route

## Shocker example

- [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]] -- target validation caught a stale address before the full scan; the corrected scan saved the Linux route
- [[OSCP/BOXES/WRITE UPS/Linux/Management|Management]] -- the raw-socket scan required a TCP-connect fallback; all output remained captured before service triage
- [[OSCP/BOXES/WRITE UPS/Linux/Cap|Cap]] -- the full service scan identified FTP, SSH, and a Gunicorn dashboard before the web evidence route was selected
- [[OSCP/BOXES/WRITE UPS/Linux/Mirai|Mirai]] -- the workspace and evidence layout were established before complete service enumeration

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
