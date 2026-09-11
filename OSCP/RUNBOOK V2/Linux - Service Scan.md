# Linux - Service Scan

**Step 3 of 50 · Linux**

*Identify the Linux services and versions that define the next branch.*

> [!tip] 💡 Follow-along mode
> You are here after the full TCP scan. Run the service scan against every open TCP port, read the complete output, and choose one row under **What did you get?**. If the target has web, go to [[Linux - Web Enum]]; if it has a versioned non-web service, go to [[Linux - Exploit Search]].

## Run this

> **Why:** This targeted scan identifies the service, version, and default-script clues needed to choose the next enumeration path.
```bash
sudo nmap -Pn -n -sC -sV -p "$OpenPorts" "$BoxIP" -oA "$BoxDir/nmap/services"
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

Focus on the line immediately after each port. The port number tells you where to connect, the service name tells you which page to open, and the version tells you whether exploit research is justified. A generic `http` result still needs [[Linux - Web Enum]]; a named product with a version can go to [[Linux - Exploit Search]] after the product is confirmed.

## What did you get?

- [ ] A web server is found → **Go to Step 5 · [[Linux - Web Enum]]**
- [ ] SSH is the only useful service → **Run `ssh $Username@$BoxIP`, then go to Step 12 · [[Linux - Shell Stabilise]] after a shell opens or Step 3B · [[Linux - SSH Brute Force]] if you have a controlled credential test**
- [ ] An unusual service has a clear version → **Go to Step 10 · [[Linux - Exploit Search]]**
- [ ] UDP 161 (SNMP) is open → **Go to Step 4 · [[Linux - SNMP Enum]]**
- [ ] TCP 53 (DNS) is open without the full AD service set → **Run dig @"$BoxIP" "$Domain" and dig axfr @"$BoxIP" "$Domain", then route any disclosed hostnames to [[Web - Virtual Host Enumeration]]**
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
- [[OSCP/BOXES/WRITE UPS/Linux/CronOS|CronOS]] -- OpenSSH, BIND, and Apache were identified; DNS was prioritised for AXFR
- [[OSCP/BOXES/WRITE UPS/Linux/Bratarina|Bratarina]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/clamAV|clamAV]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/Pelican|Pelican]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- Apache and OpenSSH service identification
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- Apache and OpenSSH service identification
- [[OSCP/BOXES/WRITE UPS/Linux/Dawn2|Dawn2]] -- Apache plus two unrecognised custom TCP services
- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]] -- Apache 2.4.18 identified on the only open TCP service
- [[OSCP/BOXES/WRITE UPS/Linux/Jarvis|Jarvis]] -- Apache 2.4.25, OpenSSH 7.4p1, and an unknown HTTP service identified
- [[OSCP/BOXES/WRITE UPS/Linux/SwagShop|SwagShop]] -- Apache 2.4.29 and OpenSSH 7.6p1 identified
- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]] -- Apache 2.4.6, PHP 5.4.16, and OpenSSH 7.4 identified
- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- Apache 2.4.29, PHP 5.6.32, OpenSSH 7.2, and FreeBSD identified
- [[OSCP/BOXES/WRITE UPS/Linux/Covfefe|Covfefe]] -- OpenSSH, Nginx, and Werkzeug/Python services identified, including the unusual high HTTP port
- [[OSCP/BOXES/WRITE UPS/Linux/TartarSauce|TartarSauce]] -- Apache 2.4.18 was the only exposed service; Nmap also surfaced useful `robots.txt` paths
- [[OSCP/BOXES/WRITE UPS/Linux/Valentine|Valentine]] -- OpenSSH 5.9p1, Apache 2.2.22, HTTPS, and the `valentine.htb` certificate name identified
- [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]] -- OpenSSH 7.9p1 and Nostromo 1.9.6 identified, routing to the Nostromo RCE page
- [[OSCP/BOXES/WRITE UPS/Linux/Traceback|Traceback]] -- OpenSSH 7.6p1 and Apache 2.4.29 identified, routing to web enumeration
- [[OSCP/BOXES/WRITE UPS/Linux/SolidState|SolidState]] -- OpenSSH and Apache identified alongside legacy James SMTP, POP3, NNTP, and RMA services; the slow version scan required targeted banner checks
- [[OSCP/BOXES/WRITE UPS/Linux/Knife|Knife]] -- OpenSSH 8.2p1 and Apache 2.4.41 identified, routing to PHP header and web enumeration
- [[OSCP/BOXES/WRITE UPS/Linux/DevOops|DevOops]] -- OpenSSH 7.2p2 and Gunicorn 19.7.1 identified, routing to Python-aware web enumeration
- [[OSCP/BOXES/WRITE UPS/Linux/Mirai|Mirai]] -- OpenSSH, dnsmasq, lighttpd, Plex, and UPnP services identified, routing to IoT and web fingerprinting

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
