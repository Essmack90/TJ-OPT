---
box_sources: [Escape]
---

# Port Triage

**Step 2 of 50 · Universal**

*Read the full-port result and decide whether the target is an AD domain controller, standalone Windows host, or Linux host.*

> [!tip] 💡 Follow-along mode
> You are here after the full TCP scan. Read the saved result, write down every open port, and choose the first matching row under **What did you get?**. Do not choose a branch from the machine description alone.

## Run this

> **Why:** Port combinations reveal the likely role of the host. This is a routing decision, not a vulnerability conclusion; the next service scan confirms the product and version.
```bash
ScanFile="$BoxDir/nmap/allports.nmap"
[ -f "$ScanFile" ] || ScanFile="$BoxDir/nmap/allports.txt"
sed -n '1,240p' "$ScanFile"
```

## Example output

Linux box:
```
22/tcp  open  ssh
80/tcp  open  http
```

Standalone Windows (no AD ports — web + SMB + RDP):
```
80/tcp   open  http
443/tcp  open  https
445/tcp  open  microsoft-ds
3389/tcp open  ms-wbt-server
```

Web-only (no SSH, no SMB, no AD):
```
80/tcp  open  http
443/tcp open  https
```

AD / Domain Controller (the combination of 88 + 389 + 445 is the tell):
```
53/tcp   open  domain
88/tcp   open  kerberos-sec
389/tcp  open  ldap
445/tcp  open  microsoft-ds
5985/tcp open  wsman
```

Focus on combinations, not isolated ports. SSH plus HTTP is a Linux-style starting point, web plus SMB/RDP without Kerberos is usually standalone Windows, and Kerberos plus LDAP plus SMB is an AD route. A web-only result does not identify the operating system yet, so use the banner and page behaviour to choose the web branch.

The next move is to run one targeted service scan with the actual open ports. Do not start exploitation from this table alone.

## What did you get?

- [ ] Ports 53, 88, 389, 445, or 5985 are open together → **Treat it as AD and go to Step 34 · [[AD - Service Scan]]**
- [ ] Windows services are open but the AD set is absent → **Treat it as standalone Windows and go to Step 22 · [[Windows - Service Scan]]**
- [ ] SSH or common Linux services are open → **Treat it as Linux and go to Step 3 · [[Linux - Service Scan]]**
- [ ] Only web ports are open → **Run `nmap -sV -p80,443 $BoxIP` and go to Step 5 · [[Linux - Web Enum]] for Apache/PHP or Step 23 · [[Windows - Web Enum]] for IIS/Windows services**
- [ ] UDP 161 is open → **Run [[Linux - SNMP Enum|SNMP Enumeration]] and preserve the walk as private loot**
- [ ] UDP 500 is open as IKE or ISAKMP → **Run Step 2A · [[Windows - IKE-IPSec Transport]] before concluding that TCP is filtered**

## Notes

Port 88 is Kerberos. Ports 389 and 3268 are LDAP or Global Catalog. Port 5985 is WinRM.

UDP results are a second routing dimension. An IKE or ISAKMP response can indicate that IPSec is hiding the TCP service surface, while SNMP may disclose the material needed to authenticate that policy.

## Gotcha

> [!warning] 💡
> Do not decide the operating system from one port. Use the service combination and confirm it with the service scan.
## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/CronOS|CronOS]] -- SSH, DNS, and Apache routed to Linux service and web enumeration
- *(no write-up yet)*
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- SSH and Apache identified as a Linux service combination
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- SSH and Apache identified as a Linux service combination
- [[OSCP/BOXES/WRITE UPS/Linux/Dawn2|Dawn2]] -- Apache plus two unrecognised custom TCP services classified for follow-up
- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]] -- only HTTP was exposed, so the Linux web branch was selected
- [[OSCP/BOXES/WRITE UPS/Linux/Jarvis|Jarvis]] -- SSH and Apache identified as a Linux service combination
- [[OSCP/BOXES/WRITE UPS/Linux/SwagShop|SwagShop]] -- SSH and Apache identified as a Linux service combination
- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]] -- SSH and Apache identified as a Linux service combination
- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- SSH and Apache on FreeBSD identified as a Linux-style service combination
- [[OSCP/BOXES/WRITE UPS/Linux/Valentine|Valentine]] -- SSH, HTTP, and HTTPS identified as a Linux service combination
- [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]] -- SSH and Nostromo HTTP identified as a Linux service combination
- [[OSCP/BOXES/WRITE UPS/AD/Active|Active]] -- AD service combination routed to the domain-controller branch
- [[OSCP/BOXES/WRITE UPS/Linux/SolidState|SolidState]] -- SSH, Apache, SMTP, POP3, NNTP, and James RMA identified as a Linux service combination
- [[OSCP/BOXES/WRITE UPS/Windows/Conceal|Conceal]] -- filtered TCP result routed to UDP SNMP and IKE/IPSec enumeration
- [[OSCP/BOXES/WRITE UPS/Windows/Bastard|Bastard]] -- standalone Windows web and RPC ports routed to the IIS branch
- [[OSCP/BOXES/WRITE UPS/Linux/Knife|Knife]] -- SSH and Apache routed to the Linux web branch
- [[OSCP/BOXES/WRITE UPS/Linux/DevOops|DevOops]] -- SSH plus port 5000 routed to Linux web enumeration
- [[OSCP/BOXES/WRITE UPS/Windows/Love|Love]] -- Apache/PHP plus SMB, WinRM, MariaDB, and RPC routed to standalone Windows web enumeration
- [[OSCP/BOXES/WRITE UPS/Windows/Optimum|Optimum]] -- HTTP-only results were classified as a standalone Windows web route after HFS fingerprinting
- [[OSCP/BOXES/WRITE UPS/Windows/Legacy|Legacy]] -- the 135/139/445 combination routed directly to Windows RPC/SMB enumeration and manual exploit research
- [[OSCP/BOXES/WRITE UPS/Linux/Busqueda|Busqueda]] -- SSH plus Apache routed to hostname-aware web enumeration, then a Python application and local Docker branch

## Shocker example

- [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]] -- HTTP plus SSH on a non-standard port routed into Linux service and CGI enumeration
- [[OSCP/BOXES/WRITE UPS/Linux/Management|Management]] -- mixed web, SSH, RMI, and directory-service ports routed into hostname-aware Linux web enumeration before application-specific exploit research
- [[OSCP/BOXES/WRITE UPS/Linux/Cap|Cap]] -- FTP, SSH, and HTTP were classified before the dashboard and PCAP branch was selected
- [[OSCP/BOXES/WRITE UPS/Linux/Covfefe|Covfefe]] -- the unusual high HTTP port and SSH combination routed to Nginx/Werkzeug web enumeration
- [[OSCP/BOXES/WRITE UPS/Linux/Mirai|Mirai]] -- SSH, DNS, HTTP, UPnP, and Plex were classified before product-aware web enumeration

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - SNMP Enum]]
- [[Windows - IKE-IPSec Transport]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
