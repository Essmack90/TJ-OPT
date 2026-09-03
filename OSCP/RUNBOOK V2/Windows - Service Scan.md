# Windows - Service Scan

**Step 22 of 50 · Windows**

*Identify IIS, SMB, RDP, and unusual Windows services before choosing the next branch.*

## Run this

> **Why:** This targeted scan identifies the service, version, and default-script clues needed to choose the next enumeration path.
```bash
sudo nmap -sC -sV -p $OpenPorts $BoxIP -oA $BoxDir/nmap/services
```

## Example output

Web + SMB (typical standalone Windows):
```
80/tcp   open  http         Microsoft IIS httpd 10.0
|_http-title: IIS Windows Server
|_http-server-header: Microsoft-IIS/10.0
445/tcp  open  microsoft-ds Windows Server 2019 Standard 17763
| smb2-security-mode:
|   3.1.1:
|     Message signing enabled but not required
```

Web + SMB + RDP + WinRM (fully exposed):
```
80/tcp   open  http          Apache httpd 2.4.41 (Win64) PHP/7.2.28
|_http-title: MegaShopping
22/tcp   open  ssh           OpenSSH for_Windows_8.1
443/tcp  open  ssl/http      Apache httpd 2.4.41
445/tcp  open  microsoft-ds  Windows Server 2019
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0
```

Key things to note from the scan output:
- **IIS version** (`IIS httpd 10.0` = Server 2016/2019, `7.5` = Server 2008) → helps date the box
- **Apache on Windows** (`Win64`) → non-IIS web stack, likely PHP app, look for PHP vulns
- **`http-title`** → names the application without opening a browser
- **SMB signing `not required`** → credential relay attacks are possible (not OSCP exam focus but worth noting)
- **OS string under port 445** → confirms exact Windows Server version
- **Port 5985 open** → WinRM available, valid creds = shell via evil-winrm
## What did you get?

- [ ] Web is open on 80 or 443 → **Go to Step 23 · [[Windows - Web Enum]]**
- [ ] Apache/PHP is open on an alternate port such as 8080 → **Go to Step 23 · [[Windows - Web Enum]] and include PHP paths and upload handlers**
- [ ] SMB is open → **Go to Step 25 · [[Windows - SMB Enum]]**
- [ ] An unusual service has a clear version → **Go to Step 26 · [[Windows - Exploit Search]]**
- [ ] No useful service is identified → **Return to Step 2 · [[Port Triage]]**

## Notes

Use `$OpenPorts` from the full scan.

## Gotcha

> [!warning] 💡
> A version banner narrows the search but does not prove a vulnerability.
## Seen in
- [[OSCP/BOXES/WRITE UPS/Windows/Jerry|Jerry]] -- Windows technique reference
- [[OSCP/BOXES/WRITE UPS/Windows/Netmon|Netmon]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]] -- Apache/PHP on TCP/8080

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
