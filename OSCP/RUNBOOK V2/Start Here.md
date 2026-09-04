# Start Here

**Step 1 of 50 · Universal**

*Initialise the box workspace, set the variables, and run the full TCP scan.*

## Run this

> **Why:** A full TCP scan finds every open port, including non-standard ports, so a service that is easy to miss does not become a missed foothold.

Run this page once at the beginning of a box. `boxstart` creates the working folders and saves the target variables; the Nmap command then finds every TCP service so the next page can choose the right path.

```bash
boxstart $BoxName $BoxIP htb
boxset BoxName $BoxName
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/HackTheBox/$BoxName
boxset Domain $Domain
sudo nmap -Pn -n -sS -p- --min-rate 5000 $BoxIP -oN $BoxDir/nmap/allports.txt
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
- *(no write-up yet)*
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- full TCP scan and helper workspace initialization
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- full TCP scan and helper workspace initialization
- [[OSCP/BOXES/WRITE UPS/Linux/Dawn2|Dawn2]] -- full TCP scan and helper workspace initialization
- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]] -- full TCP scan and helper workspace initialization
- [[OSCP/BOXES/WRITE UPS/Linux/Jarvis|Jarvis]] -- full TCP scan and helper workspace initialization
- [[OSCP/BOXES/WRITE UPS/Linux/SwagShop|SwagShop]] -- full TCP scan and helper workspace initialization
- [[OSCP/BOXES/WRITE UPS/AD/Active|Active]] -- full TCP scan and AD workspace initialization

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
