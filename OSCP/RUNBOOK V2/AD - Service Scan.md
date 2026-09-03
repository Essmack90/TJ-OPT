# AD - Service Scan

**Step 34 of 50 · AD**

*Identify the domain, FQDN, host details, and clock skew before attacking AD services.*

## Run this

> **Why:** This targeted scan identifies the service, version, and default-script clues needed to choose the next enumeration path.
```bash
sudo nmap -sC -sV -p 53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389 $BoxIP -oA $BoxDir/nmap/services
```

## Example output

```
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP
| ldap-rootdse: DNS name: DC01.htb.local
445/tcp  open  microsoft-ds  Windows Server 2019
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0
| clock-skew: 6h53m09s
```

Key things to extract from this scan:
- **LDAP DNS name** (`DC01.htb.local`) → gives you `$FQDN` and `$Domain` (`htb.local`) in one line
- **Clock skew** → anything over 5 minutes means go straight to [[AD - Clock Sync]] before anything else
- **Port 5985 open** → WinRM is available; valid creds = evil-winrm shell
- **Port 80/443 also open** → web app alongside AD; check for credentials or username leaks before roasting
## What did you get?

- [ ] Domain and FQDN are shown → **Set `$Domain` and `$FQDN`, then go to Step 35 · [[AD - Clock Sync]]**
- [ ] IIS or another HTTP service is open → **Run `curl -I http://$BoxIP/` and record the `Server` header, then go to Step 35 · [[AD - Clock Sync]]**
- [ ] Clock skew is reported → **Go to Step 35 · [[AD - Clock Sync]]**
- [ ] The scan shows no AD services → **Go back to Step 2 · [[Port Triage]]**

## Notes

Record the hostname and domain in the variables before using Kerberos or LDAP.

## Gotcha

> [!warning] 💡
> A valid domain credential can fail when the local clock is outside Kerberos tolerance. Treat clock skew as an immediate action.
## Seen in
- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- AD technique reference
- [[OSCP/BOXES/WRITE UPS/AD/Sauna|Sauna]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/AD/Return|Return]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/AD/Active|Active]] -- DNS, Kerberos, LDAP, SMB, Global Catalog, and DC host details identified

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
