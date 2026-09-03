# Port Triage

**Step 2 of 50 · Universal**

*Read the full-port result and decide whether the target is an AD domain controller, standalone Windows host, or Linux host.*

## Run this

> **Why:** This targeted scan identifies the service, version, and default-script clues needed to choose the next enumeration path.
```bash
sed -n '1,240p' $BoxDir/nmap/allports.txt
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
## What did you get?

- [ ] Ports 53, 88, 389, 445, or 5985 are open together → **Treat it as AD and go to Step 34 · [[AD - Service Scan]]**
- [ ] Windows services are open but the AD set is absent → **Treat it as standalone Windows and go to Step 22 · [[Windows - Service Scan]]**
- [ ] SSH or common Linux services are open → **Treat it as Linux and go to Step 3 · [[Linux - Service Scan]]**
- [ ] Only web ports are open → **Run `nmap -sV -p80,443 $BoxIP` and go to Step 5 · [[Linux - Web Enum]] for Apache/PHP or Step 23 · [[Windows - Web Enum]] for IIS/Windows services**

## Notes

Port 88 is Kerberos. Ports 389 and 3268 are LDAP or Global Catalog. Port 5985 is WinRM.

## Gotcha

> [!warning] 💡
> Do not decide the operating system from one port. Use the service combination and confirm it with the service scan.
## Seen in
- *(no write-up yet)*
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- SSH and Apache identified as a Linux service combination
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- SSH and Apache identified as a Linux service combination
- [[OSCP/BOXES/WRITE UPS/Linux/Dawn2|Dawn2]] -- Apache plus two unrecognised custom TCP services classified for follow-up
- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]] -- only HTTP was exposed, so the Linux web branch was selected
- [[OSCP/BOXES/WRITE UPS/AD/Active|Active]] -- AD service combination routed to the domain-controller branch

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
