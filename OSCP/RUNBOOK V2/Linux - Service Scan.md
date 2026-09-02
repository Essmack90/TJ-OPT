# Linux - Service Scan

**Step 3 of 50 · Linux**

*Identify the Linux services and versions that define the next branch.*

## Run this

> **Why:** This targeted scan identifies the service, version, and default-script clues needed to choose the next enumeration path.
```bash
sudo nmap -sC -sV -p $OpenPorts $BoxIP -oA $BoxDir/nmap/services
```

## Example output

Web + SSH (most common Linux):
```
22/tcp  open  ssh   OpenSSH 7.9p1 Debian 10 (protocol 2.0)
80/tcp  open  http  Apache httpd 2.4.38 ((Debian))
| http-title: Site doesn't have a title
```

Database exposed (MySQL on 3306):
```
22/tcp    open  ssh    OpenSSH 7.6p1
80/tcp    open  http   Apache httpd 2.4.29
3306/tcp  open  mysql  MySQL 5.7.29
```

Mail server (SMTP on 25):
```
25/tcp  open  smtp  Postfix smtpd
| smtp-commands: hostname.local, PIPELINING, SIZE 10240000, VRFY, ETRN
22/tcp  open  ssh   OpenSSH 7.4p1
```

Key things to note from the scan output:
- **Exact version numbers** → paste into [[Linux - Exploit Search]]
- **OS/distro in SSH banner** → helps narrow kernel exploit candidates
- **`http-title`** → gives away the app name before you open a browser
- **Script output under a port** → nmap `-sC` runs default scripts; read everything under each port
## What did you get?

- [ ] A web server is found → **Go to Step 5 · [[Linux - Web Enum]]**
- [ ] SSH is the only useful service → **Run `ssh $Username@$BoxIP`, then go to Step 12 · [[Linux - Shell Stabilise]] after a shell opens or Step 3B · [[Linux - SSH Brute Force]] if you have a controlled credential test**
- [ ] An unusual service has a clear version → **Go to Step 10 · [[Linux - Exploit Search]]**
- [ ] UDP 161 (SNMP) is open → **Go to Step 4 · [[Linux - SNMP Enum]]**
- [ ] Port 21 (FTP) is open → **Go to Step 3A · [[Linux - FTP Enumeration]]**
- [ ] SSH is open and a username list or recovered password exists → **Go to Step 3B · [[Linux - SSH Brute Force]] when controlled testing is justified**
- [ ] Port 25 (SMTP) is open → **Run `nc $BoxIP 25` and grab the banner; note the exact version for Step 10 · [[Linux - Exploit Search]]**
- [ ] No version is clear → **Go to Step 5 · [[Linux - Web Enum]]**

## Notes

Use `$OpenPorts` for the ports found by the full scan. Always run a UDP scan in parallel: `sudo nmap -sU --top-ports 100 $BoxIP` — SNMP (161) is easy to miss on TCP-only scans.

## Gotcha

> [!warning] 💡
> A service version alone is not an exploit. Confirm the product and version before searching.

## Custom services without banners

When a focused scan labels a TCP service as `unknown`, `tcpwrapped`, or a generic protocol, do not discard it. Record the port and check the web application for a downloadable client or server binary.

> **Why:** A custom binary often has no useful banner, but its leaked executable can reveal the protocol terminator and make offline crash analysis possible.
```bash
curl -s "http://$BoxIP/" -o "$BoxDir/loot/index.html"
```

## Additional routing

- [ ] A custom service has no banner → **Record its port, check the web root for a client/archive, and if a binary is disclosed go to Step 5 · [[Linux - Web Enum]] before attempting repeated connections**
- [ ] A leaked binary is obtained → **Run `file $BoxDir/loot/$File`, then go to Step 10 · [[Linux - Exploit Search]] for offline analysis**
## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/Bratarina|Bratarina]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/clamAV|clamAV]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/Pelican|Pelican]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- Apache and OpenSSH service identification
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- Apache and OpenSSH service identification
- [[OSCP/BOXES/WRITE UPS/Linux/Dawn2|Dawn2]] -- Apache plus two unrecognised custom TCP services
- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]] -- Apache 2.4.18 identified on the only open TCP service

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
